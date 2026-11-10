/* App settings. Nothing here is secret: a Google client ID is public by design.
   Paste the OAuth client ID between the quotes once it exists in Google Cloud Console. */
window.APP_CONFIG = {
  clientId: "138139183215-r7laorkobflp9f552o64f0c076j5395o.apps.googleusercontent.com",
  scope: "https://www.googleapis.com/auth/spreadsheets.readonly",
  /* Writing to a Sheet is switched off in this version. Turning it on also needs the wider
     "spreadsheets" scope above and a new consent from each person. */
  allowWrites: false
};
