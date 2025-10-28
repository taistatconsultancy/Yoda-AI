# Firebase Configuration Setup

## How to Get Firebase Web App Configuration

### Step 1: Go to Firebase Console
1. Visit [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **ai-assistant-f13ce**

### Step 2: Add Web App
1. Click the gear icon ⚙️ next to "Project Overview"
2. Select **"Project settings"**
3. Scroll down to **"Your apps"** section
4. Look for the **"</>"** icon (Web app)
5. Click on it

### Step 3: Register App
1. **App nickname**: Enter "YodaAI" or any name you prefer
2. Check **"Also set up Firebase Hosting"** (optional)
3. Click **"Register app"**

### Step 4: Copy Configuration
You'll see a configuration object like this:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "ai-assistant-f13ce.firebaseapp.com",
  projectId: "ai-assistant-f13ce",
  storageBucket: "ai-assistant-f13ce.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890"
};
```

### Step 5: Update `app/ui/yodaai-app.html`

Find this section (around line 1411):

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "ai-assistant-f13ce.firebaseapp.com",
  projectId: "ai-assistant-f13ce",
  storageBucket: "ai-assistant-f13ce.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID_HERE",
  appId: "YOUR_APP_ID_HERE"
};
```

Replace the placeholder values:
- Replace `"YOUR_API_KEY_HERE"` with your actual API key
- Replace `"YOUR_SENDER_ID_HERE"` with your actual messaging sender ID
- Replace `"YOUR_APP_ID_HERE"` with your actual app ID

### Step 6: Save and Test

1. Save the file
2. Restart the server (if it's not auto-reloading)
3. Go to http://localhost:8000
4. Click "Sign in with Google"
5. You should see the Google sign-in popup!

## Example

Here's what it should look like after you add your values:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyB3*********************",
  authDomain: "ai-assistant-f13ce.firebaseapp.com",
  projectId: "ai-assistant-f13ce",
  storageBucket: "ai-assistant-f13ce.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456"
};
```

## What Happens Next

1. User clicks "Sign in with Google"
2. Firebase shows Google sign-in popup
3. User selects their Google account
4. Firebase returns user info
5. Backend verifies token and creates user in Neon database
6. User is logged into the app

## Troubleshooting

### Error: "Firebase is not defined"
- Make sure Firebase SDK scripts are loaded in the `<head>` section
- Check browser console for errors

### Error: "auth/invalid-api-key"
- Double-check your API key is correct
- Make sure there are no extra spaces or quotes

### Error: "auth/unauthorized-domain"
- Add your domain to Firebase Authorized domains
- Go to Authentication → Settings → Authorized domains
- Add `localhost`

## Current Status

✅ Firebase SDK loaded  
✅ Firebase initialization code added  
✅ Google sign-in function implemented  
📋 **Remaining**: Add Firebase config values
