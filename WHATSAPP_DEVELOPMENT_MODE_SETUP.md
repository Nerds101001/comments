# WhatsApp Business API - Development Mode Setup

## Important: Your App is in Development Mode

Development mode has specific limitations and requirements:

---

## Development Mode Limitations

1. **Test Phone Numbers Only**
   - You can ONLY send messages to phone numbers that are registered as test numbers
   - You cannot send to any random phone number (including Mukul's number)
   - Maximum 5 test phone numbers allowed

2. **Token Requirements**
   - Temporary tokens from developer console work fine
   - Tokens expire in 24 hours
   - Need to regenerate daily for testing

3. **Message Limits**
   - Limited to 250 conversations per day
   - Only test numbers can receive messages

---

## How to Add Test Phone Numbers

### Step 1: Add Mukul's Number as Test Number

1. **Go to WhatsApp Developer Console:**
   ```
   https://developers.facebook.com/apps/974929091900005/whatsapp-business/wa-dev-console/
   ```

2. **Find "Phone numbers" section** in the left sidebar

3. **Click "Add phone number"** or "Manage phone numbers"

4. **Add test numbers:**
   - Click "Add phone number"
   - Enter: `+91 82644 09000` (Mukul's number)
   - Click "Send code"
   - Enter the verification code received on WhatsApp
   - Click "Verify"

5. **Repeat for other key numbers** (up to 5 total):
   - Your own number for testing
   - Any other admin/manager numbers

### Step 2: Get a Fresh Temporary Token

1. **In the same console**, find "Temporary access token"

2. **Click "Copy"** button

3. **Paste the token here** and I'll update the .env file

---

## Alternative: Switch to Live Mode

If you want to send messages to all 93 reps without restrictions:

### Requirements for Live Mode:

1. **Business Verification:**
   - Your Facebook Business Manager must be verified
   - Requires business documents (registration, tax ID, etc.)
   - Takes 1-3 business days

2. **App Review:**
   - Submit your app for review
   - Explain your use case (AI sales nudges)
   - Show how you'll use WhatsApp messaging
   - Takes 1-2 weeks typically

3. **Display Name Approval:**
   - Your business display name must be approved
   - Shows as sender name in WhatsApp

### To Start Live Mode Process:

1. Go to: https://developers.facebook.com/apps/974929091900005/app-review/
2. Click "Request" for `whatsapp_business_messaging` permission
3. Fill out the form explaining your use case
4. Submit for review

---

## Recommended Approach for Now

**For immediate testing:**

1. ✅ Add Mukul's number (+91 82644 09000) as a test number
2. ✅ Add your own number as a test number
3. ✅ Get a fresh temporary token
4. ✅ Test the system with these 2 numbers
5. ✅ Verify everything works

**For production (sending to all 93 reps):**

1. Start the Business Verification process
2. Submit app for review
3. Wait for approval (1-3 weeks total)
4. Switch to live mode
5. Generate permanent token
6. Send to all reps

---

## Current Status

- ❌ App is in Development Mode
- ❌ Cannot send to Mukul's number (not registered as test number)
- ❌ Token might be valid but restricted to test numbers only

---

## Next Steps - Choose One:

### Option A: Quick Test (Today)
1. Add Mukul's number as test number
2. Get fresh temporary token
3. Test immediately

### Option B: Production Ready (2-3 weeks)
1. Start business verification
2. Submit app for review
3. Wait for approval
4. Go live with all 93 reps

---

## What Should We Do?

Please let me know:
1. Do you want to add test numbers and test now? (Option A)
2. Or should we start the live mode approval process? (Option B)
3. Or both - test now while waiting for approval?

I recommend **Option 3** - add test numbers for immediate testing while starting the approval process in parallel.
