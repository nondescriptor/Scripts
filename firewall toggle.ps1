# This scripts simply toggles firewall rules on/off

# Ensure messageboxes appear outside of ISE
Add-Type -AssemblyName PresentationFramework

# It's generally better to use the Filter parameter than Where-Object or where() because the Filter parameter passes instructions to .NET to limit output at the provider level, rather than having to pull all of those objects out and then filtering the output at the pipeline level. However, for this use-case, it really doesn't matter.

# Check if property returns false
$condition = Get-NetFirewallRule -DisplayName '<rule name>' | Where-Object {$_.Enabled -eq 'false'}

# Format pop-up message
$Title = 'Warning'
$Icon = [System.Windows.MessageBoxImage]::Warning
$Buttons = 'YesNoCancel'

# If it's disabled, enable it and vice-versa.
if ($condition) {
	$Message = 'Firewall rule is currently disabled. Would you like to enable it?'
	$UserInput = [System.Windows.MessageBox]::Show($Message,$Title,$Buttons,$Icon)
	switch ($UserInput) {
		'Yes' {Enable-NetFirewallRule -DisplayName '<rule name>'}
		'No' {Exit}
		'Cancel' {Exit}
	}
}
else {
	$Message = 'Firewall rule is currently enabled. Would you like to disable it?'
	$UserInput = [System.Windows.MessageBox]::Show($Message,$Title,$Buttons,$Icon)
	switch ($UserInput) {
		'Yes' {Disable-NetFirewallRule -DisplayName '<rule name>'}
		'No' {Exit}
		'Cancel' {Exit}
	}
}
