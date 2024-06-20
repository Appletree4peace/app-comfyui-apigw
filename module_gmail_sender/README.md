# Gmail Sender

The `gmail_sender` module provides a simple interface to send emails using the Gmail API. This module abstracts away the complexities of Gmail API integration, allowing for easy and quick email sending with just a few lines of Python code.

## Prerequisites

- Python 3.x
- You must have a Google Cloud Project with Gmail API enabled. See [PREPARE_GOOGLE_ACCOUNT.md](PREPARE_GOOGLE_ACCOUNT.md)
- Create and download a service account key and name it `gcp-svc-acc-key.json`. This will be used to authenticate your application.

## Installation

1. Clone the repository:

    ```bash
    git clone git@github.com:jeffreycai/module-gmail-sender.git
    cp module-gmail-sender [your-project-dir]
    ```

2. Install the required Python packages:

    ```bash
    cd module-gmail-sender.git
    pip install -r requirements.txt
    ```

3. Place the `gcp-svc-acc-key.json` service account key file in the module root dir.

## Usage

To use the `GmailSender` class in your application:

1. Import the module:

    ```python
    from gmail_sender import GmailSender
    ```

2. Create an instance of the `GmailSender` class:

    ```python
    sender = GmailSender()
    ```

3. Use the `send` method of the created object to send an email:

    ```python
    sender.send('Your Subject Here', '<b>Your HTML Message Content Here</b>')
    ```

By default, the sender and recipient addresses are set to the default values defined in the `GmailSender` class. You can override these by passing them as arguments to the `send` method.

## Customization

If you want to customize the sender, recipient, or any other default settings:

- Adjust the class attributes of `GmailSender` or pass the desired values as arguments when creating an instance of `GmailSender` or invoking the `send` method.

## Example

Here's a simple usage example:

```python
from gmail_sender import GmailSender

def main():
    sender = GmailSender()
    sender.send('Test Subject', '<b>This is a test message.</b>')

if __name__ == '__main__':
    main()
```

## Troubleshooting

If you encounter issues:

- Ensure the Gmail API is enabled for your Google Cloud Project.
- Verify that the `gcp-svc-acc-key.json` service account key file is correctly placed in your directory.
- Ensure that you have given appropriate permissions to the service account in the Google Cloud Console, and that the email address associated with it has the necessary Gmail API scopes.

## License

This project is licensed under the MIT License.
