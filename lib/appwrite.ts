import { Client, Databases, Account } from 'appwrite';

export const client = new Client();

client
    .setEndpoint(process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT || 'https://nyc.cloud.appwrite.io/v1')
    .setProject(process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID || '694f9a5d00376355b3a9');

export const databases = new Databases(client);
export const account = new Account(client);

export const APPWRITE_CONFIG = {
    DATABASE_ID: process.env.NEXT_PUBLIC_APPWRITE_DATABASE_ID || '694f9a8e00337e542bce',
    COLLECTION_ID: 'otp_logs',
    CMD_COLLECTION_ID: 'command_queue',
};
