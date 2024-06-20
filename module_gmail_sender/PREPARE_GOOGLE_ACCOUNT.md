# Setting Up Google Account for API Email Sending

This guide will walk you through the process of creating a service account with the necessary permissions to send mail via the Gmail API.

## Steps

### 1. Create the Service Account

- Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
- Select your project.
- Go to "IAM & Admin" > "Service accounts".
- Click "CREATE SERVICE ACCOUNT".
- Fill in the details for your service account, and click "CREATE".
- You do not need to grant this service account access to any roles, so click "CONTINUE" and then "DONE".

### 2. Generate a JSON Key for the Service Account

- In the service accounts list, find the service account that you just created, and click on the email address to go to its details page.
- Click "ADD KEY" > "Create new key".
- Select "JSON", and click "CREATE". This will generate a JSON key for your service account and download it to your machine. Keep this file secure.

### 3. Enable the Gmail API

- Go to "APIs & Services" > "Library".
- Search for "Gmail API", and click on it.
- Click "ENABLE".

### 4. Delegate Domain-Wide Authority to Your Service Account

This step allows the service account to send emails on behalf of users in your Google Workspace domain. This must be done by an administrator of your Google Workspace domain.

- The administrator should go to their [Google Workspace admin console](https://admin.google.com/).
- Go to "Security" > "API controls".
- In the "Domain wide delegation" pane, click "MANAGE DOMAIN WIDE DELEGATION".
- Click "ADD NEW".
- In the "Client ID" field, enter the client ID of your service account. You can find this in the details page of your service account in the Cloud Console. It's a long number.
- In the "OAuth Scopes" field, enter:
    - https://www.googleapis.com/auth/gmail.readonly # Read-only access to Gmail; read emails and labels.
    - https://mail.google.com/ # Full access to Gmail; read, compose, send, delete emails.
    - https://www.googleapis.com/auth/gmail.modify # Read and modify Gmail but not delete; manage labels.
    - https://www.googleapis.com/auth/gmail.compose # Compose and send Gmail; create, read, update, send emails.
    - https://www.googleapis.com/auth/gmail.send # Send Gmail; send emails without reading or modifying inbox.
    - https://www.googleapis.com/auth/gmail.insert # Insert mail into Gmail; insert emails into mailbox.
    - https://www.googleapis.com/auth/gmail.labels # Manage mailbox labels in Gmail.
    - https://www.googleapis.com/auth/gmail.metadata # View Gmail message metadata; headers and labels, not body.
    - https://www.googleapis.com/auth/gmail.settings.basic # Manage basic Gmail settings; filters, labels.
    - https://www.googleapis.com/auth/gmail.settings.sharing # Manage all Gmail settings; forwarding rules, aliases.
- Click "AUTHORIZE".

You should now have a service account that is authorized to send mail on behalf of users in your Google Workspace domain. You can use the JSON key that you downloaded to authenticate this service account in your application.

**Note:** Keep your service account credentials secure, as they can be used to gain access to your Google Workspace domain. Also, ensure that you adhere to Google's terms of service and usage policies when sending mail via the Gmail API.
