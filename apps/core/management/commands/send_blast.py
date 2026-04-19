from django.core.management.base import BaseCommand
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Sends a custom HTML email blast to all active users.'

    def handle(self, *args, **kwargs):
        # 1. Grab all users who actually have an email and are active
        users = User.objects.filter(is_active=True).exclude(email='')
        
        if not users.exists():
            self.stdout.write(self.style.WARNING("No active users found with email addresses."))
            return

        self.stdout.write(f"Preparing to send email to {users.count()} users...")

        # 2. Setup the email content
        subject = "Huge Updates to CineVerse! 🚀"
        from_email = "hey.cineverse@gmail.com" # Change this to your actual sender email

        # 3. Open a SINGLE connection to the email server (Massive performance boost)
        connection = get_connection()
        connection.open()

        success_count = 0
        emails_to_send = []

        # 4. Build the emails
        for user in users:
            # Pass the user object to the template so you can say "Hi [Username]"
            context = {'user': user}
            
            # Render the HTML template
            html_content = render_to_string('emails/newsletter.html', context)
            
            # Create a plain-text version automatically
            text_content = strip_tags(html_content)

            # Construct the message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[user.email],
                connection=connection # Use the persistent connection
            )
            msg.attach_alternative(html_content, "text/html")
            emails_to_send.append(msg)

        # 5. Fire them all off
        try:
            self.stdout.write("Sending emails...")
            success_count = connection.send_messages(emails_to_send)
            self.stdout.write(self.style.SUCCESS(f"Successfully sent {success_count} emails!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending emails: {e}"))
        finally:
            connection.close()