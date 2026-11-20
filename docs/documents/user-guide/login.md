# Login

How to sign in and out of the web app.

## Sign in

Every section of the app needs a signed-in user. Without a session the app opens the login page, `/login`. After a successful login the app opens the section you asked for, or Home when you came to the login page directly.

1. Enter your email and your password.
2. Press "Accedi".

A wrong email or password shows "Email o password non corretti". The message is the same for both, so it does not tell whether the email has an account.

After 5 wrong passwords on one account, the account is locked for 15 minutes. The login page then shows "Troppi tentativi, riprova tra 15 minuti". A correct password does not unlock it before the 15 minutes pass.

There is no sign-up on the login page. A new player gets an account through an [invite link](invite-links.md) from the admin.

## Session

The session lasts 30 days from your last use of the app, and each use extends it. After that the app asks for the login again. When a session ends while you use the app, the next action opens the login page.

## Sign out

The header shows your first name and last name and a logout button ("Esci"). On a narrow screen the name is hidden and the button stays. Pressing it ends the session and opens the login page.

## Forgot your password

Ask the admin for a new [invite link](invite-links.md#set-a-new-password). The link sets a new password and signs out every other session of your account.
