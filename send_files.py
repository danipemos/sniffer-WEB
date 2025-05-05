import gnupg

# Inicializa el objeto GPG
gpg = gnupg.GPG()

gpg.gen_key_input()

# Listar claves públicas
public_keys = gpg.list_keys()
print("Claves públicas:")
for key in public_keys:
    print(f"ID: {key['keyid']}, UIDs: {key['uids']}")

# Listar claves privadas (secretas)
private_keys = gpg.list_keys(secret=True)
print("\nClaves privadas:")
for key in private_keys:
    print(f"ID: {key['keyid']}, UIDs: {key['uids']}")
