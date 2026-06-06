import os
import ssl
from typing import Dict, Optional

from ldap3 import Server, Connection, ALL, SUBTREE, Tls

class LdapAuthError(Exception):
    pass

INTERNAL = {
    "host": os.getenv("LDAP_INTERNAL_HOST", "digitelcorp.com.ve"),
    "domain": os.getenv("LDAP_INTERNAL_DOMAIN", "digitelcorp.com.ve"),
    "base_dn": os.getenv("LDAP_INTERNAL_BASE", "dc=digitelcorp,dc=com,dc=ve"),
    "bind_user": os.getenv("LDAP_INTERNAL_USER", "Uconsult"),  
    "bind_password": os.getenv("LDAP_INTERNAL_PASSWORD", "M3Pa*bc88,Nene"),
    "port": int(os.getenv("LDAP_INTERNAL_PORT", 389)),
    "use_ssl": os.getenv("LDAP_INTERNAL_SSL", "true").lower() == "true",
}

EXTERNAL = {
    "host": os.getenv("LDAP_EXTERNAL_HOST", "digitelaccc.digitelcorp.com.ve"),
    "domain": os.getenv("LDAP_EXTERNAL_DOMAIN", "digitelaccc.digitelcorp.com.ve"),
    "base_dn": os.getenv("LDAP_EXTERNAL_BASE", "dc=digitelaccc,dc=digitelcorp,dc=com,dc=ve"),
    "bind_user": os.getenv("LDAP_EXTERNAL_USER", "Uconsult"),
    "bind_password": os.getenv("LDAP_EXTERNAL_PASSWORD", "M3Pa*bc88,Nene"),
    "port": int(os.getenv("LDAP_EXTERNAL_PORT", 389)),
    "use_ssl": os.getenv("LDAP_EXTERNAL_SSL", "true").lower() == "true",
}

LDAP_SERVERS = [INTERNAL, EXTERNAL]

TLS_VALIDATE = os.getenv("LDAP_TLS_VALIDATE", "none").lower()  
CA_FILE = os.getenv("LDAP_CA_FILE")  

def _tls():
    if TLS_VALIDATE == "required" and CA_FILE:
        return Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=CA_FILE, version=ssl.PROTOCOL_TLSv1_2)
    # Atención: CERT_NONE solo para pruebas. En producción usa REQUIRED + CA_FILE.
    return Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)

def _as_upn(user: str, domain: str) -> str:
    # Acepta "usuario", "DOMINIO\usuario" o "usuario@dominio"
    if "@" in user:
        return user
    if "\\" in user:
        return user  # ya viene como DOMINIO\usuario
    return f"{user}@{domain}"

def ldap_authenticate_with_service(username: str, password: str) -> Dict:
    """
    1) Bind con CUENTA DE SERVICIO (por servidor).
    2) Buscar DN del usuario (sAMAccountName=username o userPrincipalName=username@dominio).
    3) Rebind con ese DN y la contraseña proporcionada por el usuario.
    Devuelve metadata si éxito; lanza LdapAuthError si falla en ambos servidores.
    """
    if not username or not password:
        raise LdapAuthError("Usuario o contraseña vacíos.")

    last_error: Optional[str] = None

    for cfg in LDAP_SERVERS:
        host = cfg["host"]
        domain = cfg["domain"]
        base_dn = cfg["base_dn"]
        port = cfg["port"]
        use_ssl = cfg["use_ssl"]
        bind_user = cfg["bind_user"]
        bind_password = cfg["bind_password"]

        # La cuenta de servicio puede venir como "usuario" → la convertimos a UPN por defecto
        bind_identity = _as_upn(bind_user, domain)

        try:
            server = Server(host, port=port, use_ssl=use_ssl, tls=_tls(), get_info=ALL)

            # 1) Bind con cuenta de servicio
            svc_conn = Connection(server, user=bind_identity, password=bind_password,
                                  auto_bind=True, receive_timeout=8)

            # 2) Buscar DN del usuario a autenticar
            # Intentamos por UPN y sAMAccountName
            upn_candidate = _as_upn(username, domain)
            filtro = f"(|(userPrincipalName={upn_candidate})(sAMAccountName={username}))"

            svc_conn.search(
                search_base=base_dn,
                search_filter=filtro,
                search_scope=SUBTREE,
                attributes=["distinguishedName", "cn", "mail", "sAMAccountName", "userPrincipalName"]
            )

            if not svc_conn.entries:
                # Usuario no existe en este dominio/servidor → probar siguiente
                svc_conn.unbind()
                continue

            dn = str(svc_conn.entries[0].distinguishedName)
            # (Opcional) info de usuario
            info = svc_conn.entries[0]
            user_info = {
                "cn": str(info.cn) if "cn" in info else None,
                "mail": str(info.mail) if "mail" in info else None,
                "sAMAccountName": str(info.sAMAccountName) if "sAMAccountName" in info else username,
                "userPrincipalName": str(info.userPrincipalName) if "userPrincipalName" in info else upn_candidate,
                "distinguishedName": dn,
            }

            svc_conn.unbind()

            # 3) Rebind con DN + password del usuario (valida credenciales reales)
            user_conn = Connection(server, user=dn, password=password, auto_bind=True, receive_timeout=8)
            user_conn.unbind()

            return {
                "authenticated": True,
                "domain": domain,
                "server": host,
                "base_dn": base_dn,
                "user": user_info
            }

        except Exception as ex:
            last_error = f"{host} ({domain}): {ex}"
            # Continúa con el siguiente servidor (externo)

    raise LdapAuthError(f"No fue posible autenticar en LDAP con cuenta de servicio. Último error: {last_error}")