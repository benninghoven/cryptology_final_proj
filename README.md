# Secure Chat

This project implements a system enabling a group of users to chat securely. Users are registered with the chat server. When initiating a chat, the user connects to the server, enters their username and password, and if verified, their status is changed to "online". The user can then select other registered users to chat with. They can also check who else is online and invite them to join the conversation.

## Key Features

- **User Authentication**: Users log in with a username and password.
- **Online Status**: Users are marked as "online" when logged in and "offline" when disconnected.
- **Secure Key Distribution**: The server generates a symmetric key for each chat session, encrypts it using the public keys of the participating users, and distributes it securely.
- **Encryption**: All messages exchanged during the chat are encrypted using the symmetric key provided by the server.
- **Digital Signature**: Users have the option to choose between RSA or Digital Signature Algorithm for digital signature.
- **User Interaction**: Users can initiate chats, invite others, and leave conversations.

## How it Works

1. User logs in to the chat server.
2. User selects other users to chat with.
3. Server generates a symmetric key for the chat session.
4. Server encrypts the symmetric key using the public keys of the participating users and distributes it securely.
5. Users decrypt the symmetric key using their private keys.
6. Chat session begins with encrypted messages exchanged using the symmetric key.
7. Users can leave the conversation or disconnect from the server, changing their status to "offline".

## Requirements

- Programming Language: [Specify here]
- Libraries/Frameworks: [Specify here]
- Public/Private Key Pairs for Users
- Encryption Algorithm (e.g., RSA, Digital Signature Algorithm)

## Usage

[Provide instructions on how to set up and run the application.]

## Note

This implementation supports single chat sessions and ensures confidentiality and digital signature for secure communication.

## Contributors

[List of contributors or acknowledgements]

## License

[Specify the license]

## Feedback and Contributions

[Provide information on how users can give feedback or contribute to the project.]
