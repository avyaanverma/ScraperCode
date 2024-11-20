import re
import dns.resolver
from email_validator import validate_email, EmailNotValidError

def verify_email(email):
    # Check if email format is valid
    try:
        validate_email(email)
    except EmailNotValidError as e:
        print(f"Invalid email format: {email}. Error: {e}")
        return False
    
    # Extract domain from email
    domain = email.split('@')[1]
    
    # Check if the domain has MX (Mail Exchange) records
    try:
        dns.resolver.resolve(domain, 'MX')
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        print(f"Domain does not exist or has no mail servers: {domain}")
        return False
    
    print(f"Email {email} is valid!")
    return email

# # List of emails to verify
# emails = [
#     "avyaanver@gmail.com",
#     "test@123",
#     "rizwan.ur@vitbhopal.ac.in"
# ]
# verified_emails = []
# # Verify each email in the list
# for email in emails:
#   if verify_email(email): verified_emails.append(email)
# verified_emails