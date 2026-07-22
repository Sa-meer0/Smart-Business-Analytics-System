from services.auth_service import auth_service


def main():

    username = "admin"
    password = "admin123"

    full_name = "System Administrator"

    email = "admin@sbas.com"

    if auth_service.username_exists(username):

        print("Admin already exists.")

    else:

        auth_service.create_admin(

            username,

            password,

            full_name,

            email

        )

        print("Admin account created successfully.")


if __name__ == "__main__":
    main()
