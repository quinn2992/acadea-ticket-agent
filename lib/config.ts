// Base path the app is served under. The app is hosted at
// acadea.panthael.ai/ticketagent — everything (pages, API, assets) lives
// under this prefix. Both next.config.ts and the client code import
// from here so the value is single-sourced.
//
// If we later change the path (or move to the root), this is the one line
// to edit plus a redeploy.
export const BASE_PATH = "/ticketagent";
