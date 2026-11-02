> Historical instructions from the combined ZIP. The code now lives in two repositories; use this repository’s README for current setup and deployment paths.

# Start here — phone-friendly handoff

You do not need to manually upload every file.

1. Download this ZIP and attach it to the chat that has your GitHub connection.
2. Paste this message:

> Please open the attached Velora Toons project ZIP. Read HANDOFF_FOR_NEXT_CHAT.md and docs/VALIDATION.md first. Preserve the multi-file design. Run its tests, inspect the source adapter against current public pages, fix any observed issues, and push the project into a new repository in my GitHub account. Guide or perform the Vercel frontend and Render backend deployment using the connections actually available. Report the URLs and exactly what playback was verified. Do not claim that an embedded player is a direct media URL.

3. Tell that chat which **new repository name** you want, for example `velora-toons`. The ZIP contains no assumed GitHub credentials.
4. Once deployed, open the Vercel URL on your phone. If not preconfigured, open Your space, paste the Render backend address, and save.
5. Search a title, choose an episode, then choose a language/player. Tap play in the provider player. If it cannot embed, use Open player.

A source website can remove files or change its markup. No instructions file can guarantee a different assistant's capabilities or decisions, and this project does not ask it to ignore its own rules. The handoff records the technical work and remaining checks so it can continue efficiently.

**Important:** this source does not currently provide a verified direct download for the tested episodes. The app handles provider playback and offers downloads only for explicit media URLs that its adapter can verify. The lightweight deployment does not use a browser; enable the optional image only if you need non-default dynamic seasons and your host has enough memory.
