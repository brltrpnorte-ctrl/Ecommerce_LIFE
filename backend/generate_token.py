import secrets

print("Token seguro gerado:")
print(secrets.token_urlsafe(32))
print("\nAdicione este token no arquivo .env como AUTH_TOKEN")
