param(
  [Parameter(Mandatory=$true)][string]$Text,
  [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$maleSpanish = @($synth.GetInstalledVoices() | Where-Object {
  $_.VoiceInfo.Gender.ToString() -eq 'Male' -and $_.VoiceInfo.Culture.Name -like 'es*'
})
if ($maleSpanish.Count -eq 0) {
  throw 'No hay una voz masculina en español instalada. Instala una voz es-ES o es-MX y vuelve a intentar.'
}
$selected = $maleSpanish | Where-Object { $_.VoiceInfo.Name -match 'Raul' } | Select-Object -First 1
if ($null -eq $selected) { $selected = $maleSpanish | Where-Object { $_.VoiceInfo.Name -match 'Pablo' } | Select-Object -First 1 }
if ($null -eq $selected) { $selected = $maleSpanish[0] }
$synth.SelectVoice($selected.VoiceInfo.Name)
$synth.Rate = 0
$synth.Volume = 100
$synth.SetOutputToWaveFile($Output)
$synth.Speak($Text)
$synth.Dispose()
Write-Output ("VOICE_NAME=" + $selected.VoiceInfo.Name)
