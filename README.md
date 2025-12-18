# ytdl-proxy

I have a server that has some programs on it that need to use 
[yt-dlp](github.com/yt-dlp/yt-dlp) to get audio for various automations.
The problem is said server runs on OVH, which YouTube (fairly) blocks from
accessing their servers.

This program runs on a local Raspberry Pi on my home network, and is designed
to take download requests from any client on my VPN, download them using
my home wifi, then send the file back to the requester once done.

YouTube tends to patch a the ways yt-dlp downloads videos all the time and
has lots of anti-bot stuff, so it also includes a systemd service that
updates yt-dlp and ytdl-proxy nightly to keep things running smoothly
(most of the time, unless they push a breaking change).

## api
The API is a simple HTTP server with no authentication (since this runs only
over a virtual private network).

There are two methods of getting files, depending on length:

### POST `/`
Designed for small downloads that can be accomplished before the request
times out.

JSON body:
* `video` (str): link to the video
* `format` (str): resulting file format
    * mp4, mp3, etc

Returns: 
* 200 status code: The audio file as the response content
* 4xx/5xx status code: JSON
    * `error` (str): What went wrong

### POST `/async`
Designed for large downloads that should be performed asynchronously.

JSON body:
* `video` (str): link to the video
* `format` (str): resulting file format
    * mp4, mp3, etc

JSON response:
* `id` (str): ID to check on results

### GET `/async`
Checks on the completion of an async download.

Args:
* `id` (str): ID to check in on

JSON response:
* `status` (str): `PENDING`, `DONE`, `FAILED`
* `error` (str): if status is `FAILED`, what went wrong

#### POST `/async/content`
Gets the content of a `DONE` async download, then deletes it from the server.

JSON body:
* `id` (str): ID to download

Returns: 
* 200 status code: The audio file as the response content
* 4xx/5xx status code: JSON
    * `error` (str): What went wrong