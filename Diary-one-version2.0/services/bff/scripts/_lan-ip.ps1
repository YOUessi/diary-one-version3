# Dot-source this file. Sets $DiaryLanIPv4 to the Wi-Fi / 192.168 address phones can reach.
# Never pick WSL/Hyper-V (172.22.x) — Android Expo Go cannot route there.

function Get-DiaryLanIPv4 {
  $candidates = @(
    Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
      Where-Object {
        $_.IPAddress -notmatch '^(127\.|169\.254\.)' -and
        $_.InterfaceAlias -notmatch '(?i)WSL|Hyper-V|vEthernet|Loopback|Docker|Default Switch'
      }
  )
  $wifi = $candidates | Where-Object { $_.InterfaceAlias -match '(?i)WLAN|Wi-?Fi|无线' } | Select-Object -First 1
  if ($wifi) { return [string]$wifi.IPAddress }
  $home = $candidates | Where-Object { $_.IPAddress -like '192.168.*' } | Select-Object -First 1
  if ($home) { return [string]$home.IPAddress }
  $rest = $candidates | Select-Object -First 1
  if ($rest) { return [string]$rest.IPAddress }
  throw "No LAN IPv4 found. Connect Wi-Fi first."
}

$DiaryLanIPv4 = Get-DiaryLanIPv4
