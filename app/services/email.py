import os
import logging
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound

from app.core.config import settings

template_folder = "app/templates"
templates = Environment(loader=FileSystemLoader(template_folder))

class EmailService:
    _template_env = None

    @classmethod
    def _get_template_env(cls):
        """
        Initialize Jinja2 template environment if not already initialized
        """
        if cls._template_env is None:
            # Dynamically find the templates directory
            template_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..',
                'templates'
            )

            cls._template_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html'])
            )
        return cls._template_env

    @classmethod
    def render_template(cls, template_name: str, context: dict) -> str:
        """
        Render an email template

        :param template_name: Name of the template file
        :param context: Dictionary of template variables
        :return: Rendered HTML template
        """
        try:
            # Add default context variables
            default_context = {
                'company_name': 'Your Company',
                'current_year': datetime.now().year,
                **context
            }

            template_env = cls._get_template_env()
            template = template_env.get_template(template_name)
            return template.render(**default_context)
        except Exception as e:
            logging.error(f"Error rendering email template {template_name}: {e}")
            raise

    @classmethod
    def send_email(
        cls,
        to_email: str,
        subject: str,
        template_name: str,
        template_context: dict,
    ):
        """
        Send an email using a specified template via SendGrid API.

        :param to_email: Recipient email address
        :param subject: Email subject
        :param template_name: Name of the template file
        :param template_context: Dictionary of template variables
        """
        try:
            # Render HTML content
            try:
                template = templates.get_template(template_name)
                html_content = template.render(template_context)
                logging.info(f"Rendered HTML content: {html_content}")  # Log the rendered content
            except TemplateNotFound:
                logging.error(f"Template '{template_name}' not found.")
                raise ValueError(f"Template '{template_name}' does not exist.")

            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject
                    }
                ],
                "from": {"email": settings.EMAILS_FROM_NAME},
                # "from": {"email": "info@dakebfarms.com.ng"},
                "content": [
                    {
                        "type": "text/html",
                        "value": html_content
                    }
                ]
            }

            # SendGrid API endpoint
            url = "https://api.sendgrid.com/v3/mail/send"

            # Headers with API key
            headers = {
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            }

            # Make the API request
            response = requests.post(url, json=payload, headers=headers)

            # Check for errors
            if response.status_code != 202:
                logging.error(f"Failed to send email. Status code: {response.status_code}, Response: {response.text}")
                raise Exception(f"SendGrid API error: {response.text}")

            logging.info(f"Email sent successfully to {to_email}. Status code: {response.status_code}")

        except Exception as e:
            logging.error(f"Error sending email: {e}")
            raise