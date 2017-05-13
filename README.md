# trbwrk

trbwrk (pronounced "Triebwerk") is a command line client to automatically analyse unwanted Emails.

The main target is the processing of the emails for statistic purposes.

> The software is a proof of concept and is far away from any kind of production usage.

## Usage

`trbwrk.py [options]`

|Option|Description|
|-|-|
|`--json`|The results will be printed in JSON format|
|`--quiet`|No version information will be printed, will be set if `--json` is used|
|`--screenshots path`|Will save screenshots from extracted links into the folder `path`. The folder must be existing, works only if `--visitlinks`  is set|
|`--visitlinks`|Visit links to extract server headers and screenshots (if wanted)|
|`--file file`|If set together with `--json`, the JSON will be stored into the given file|
|`--attachments path`|Will save attachments into the given directory, which must be existing|
|`--timeout seconds`|Sets the timeout for download activities|
|`--whois`|Does whois queries. The Result is a text, because the TLD registrars don't use an standard format|
|`--nslookup`|Does domain searches, also extracts hoster and location|
|`--raw file`|Uses a raw dump of the email (including headers) to analyze it.|





## License

GNU Lesser General Public License v2.1