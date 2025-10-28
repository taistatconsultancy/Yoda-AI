# How to Get Firebase Web App Configuration

## Quick Steps

### 1. Go to Firebase Console
Open: https://console.firebase.google.com/project/ai-assistant-f13ce/settings/general

### 2. Scroll Down to "Your apps"
Look for the section that shows your apps (Web, iOS, Android, etc.)

### 3. Add Web App (if not exists)
- Click the **"</>"** (Web) icon
- Give it a nickname: "YodaAI" 
- Click "Register app"

### 4. Copy the Config
You'll see something like this:

```javascript
var firebaseConfig = {
  apiKey: "AIzaSyC********************************",
  authDomain: "ai-assistant-f13ce.firebaseapp.com",
  projectId: "ai-assistant-f13ce",
  storageBucket: "ai-assistant-f13ce.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456"
};
```

### 5. Update `app/ui/yodaai-app.html`

Replace lines 1412-1417 with your actual values:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyC********************************",  // ← Your actual API key
  authDomain: "ai-assistant-f13ce.firebaseapp.com",
  projectId: "ai-assistant-f13ce",
  storageBucket: "ai-assistant-f13ce.appspot.com",
  messagingSenderId: "123456789012",                    // ← Your actual ID
  appId: "1:123456789012:web:abc123def456"              // ← Your actual App ID
};
```

## If You Can't Find the Web App

If there's no web app listed in Firebase Console:

1. Click the "Add app" button (or "</>" icon)
2. Select "Web" 
3. Register the app
4. Copy the configuration values shown
5. Paste them into `app/ui/yodaai-app.html`

## Alternative: Check Project Settings

If you can't find it in "Your apps":

1. Go to: https://console.firebase.google.com/project/ai-assistant-f13ce/settings/general
2. Look for a section showing existing apps
3. If you see a web app already listed, click on it to see the config
4. If not, click "Add app" → Web

## After Updating

1. Save the file
2. Refresh the browser (Ctrl+F5 or Cmd+Shift+R)
3. Click "Sign in with Google"
4. It should work!

---

**The error you're seeing means the Firebase API key is a placeholder. Once you replace it with the real key from Firebase Console, it will work!**

