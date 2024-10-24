# This script sets the default printer, scans file as PNG, converts it to PDF and saves it to desktop

function DefaultPrinter {
	# Format pop-up message
	$Title = 'Warning'
	$Icon = [System.Windows.MessageBoxImage]::Warning
	$Buttons = 'OK'

	Write-Output 'Checking default printer...'
	$PrinterName = Get-CimInstance -ClassName Win32_Printer -Filter "Default = 'true'" |
	Select-Object -ExpandProperty Name
	$PrinterLocation = Get-CimInstance -ClassName Win32_Printer -Filter "Default = 'true'" |
	Select-Object -ExpandProperty Location

	# If it's already the default printer, do nothing; otherwise, change it.
	if ($PrinterName -like "$NameRegex*") {
		Write-Output "$PrinterName at $PrinterLocation is already the default"
	}
	elseif ($PrinterLocation -like "*$IPregex*") {
		Write-Output "$PrinterName at $PrinterLocation is already the default"
	}
	else {
		Write-Output 'Changing default printer...'
		# Search for printer by name or IP
		$PrinterName = Get-CimInstance -Class Win32_Printer | Where-Object {$_.Name -like "$NameRegex*"}
		$PrinterLocation = Get-CimInstance -Class Win32_Printer | Where-Object {$_.Location -like "*$IPregex*"}

		if ($PrinterName) {
			Write-Output 'Printer found by name'

			# Use SetDefaultPrinter instance method on printer object
			$condition = Invoke-CimMethod -InputObject $PrinterName -MethodName SetDefaultPrinter

			# Turn variables into strings for console messages
			$PrinterName = $PrinterName.Name
			$PrinterLocation = $PrinterName.Location

			if ($condition) {
				Write-Output "$PrinterName has been set as default at $PrinterLocation"
			}
			else {
				$Message = "$PrinterName could not be set as default via name"
				[System.Windows.MessageBox]::Show($Message,$Title,$Buttons,$Icon)
				Exit
			}
		}
		elseif ($PrinterLocation) {
			Write-Output 'Printer found by IP address'

			# Use SetDefaultPrinter instance method on printer object
			$condition = Invoke-CimMethod -InputObject $PrinterLocation -MethodName SetDefaultPrinter

			# Turn variables into strings for console messages
			$PrinterName = $PrinterLocation.Name
			$PrinterLocation = $PrinterLocation.Location

			if ($condition) {
				Write-Output "$PrinterName has been set as default at $PrinterLocation"
			}
			else {
				$Message = "$PrinterName could not be set as default via IP address"
				[System.Windows.MessageBox]::Show($Message,$Title,$Buttons,$Icon)
				Exit
			}
		}
		else {
			$Message = 'Printer could not be found by name or IP address'
			[System.Windows.MessageBox]::Show($Message,$Title,$Buttons,$Icon)
			Exit
		}
	}
}

function Scan {
	# Format pop-up message
	$Title = 'Warning'
	$Icon = [System.Windows.MessageBoxImage]::Warning
	$Buttons = 'OK'

	# Use WIA object hierarchy to create scanner object and connect
	$deviceManager = new-object -ComObject WIA.DeviceManager
	$device = $deviceManager.DeviceInfos.Item(1).Connect()

	# If connection was successful, scan item
	if ($device) {
		Write-Output 'Imaging device found'
		Write-Output 'Scanning now...'

		# Define image FormatID constants
		$wiaFormatBMP  = '{B96B3CAB-0728-11D3-9D7B-0000F81EF32E}'
		$wiaFormatPNG  = '{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}'
		$wiaFormatGIF  = '{B96B3CB0-0728-11D3-9D7B-0000F81EF32E}'
		$wiaFormatJPEG = '{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}'
		$wiaFormatTIFF = '{B96B3CB1-0728-11D3-9D7B-0000F81EF32E}'

		$image = $device.Items.Item(1).transfer($wiaFormatPNG)
		# The returned ImageFile object from the transfer() method has a FormatID property that specifies
		# the format that was actually used, so it doesn't always honor the request to capture
		# as a different format
		# If that's the case, the image will have to converted manually via ImageProcess
	}
	else {
		$Message = 'Cannot connect to scanner'
		[System.Windows.MessageBox]::Show($Message,$Title,$Buttons,$Icon)
		Exit
	}

	# If the image doesn't match PNG FormatID, convert it
	if ($image.FormatID -ne $wiaFormatPNG) {
		Write-Output 'Image format not PNG'
		Write-Output 'Converting now...'

		# Create copy of image
		$imageProcess = new-object -ComObject WIA.ImageProcess

		# Convert to PNG using filters
		$imageProcess.Filters.Add($imageProcess.FilterInfos.Item("Convert").FilterID)
		$imageProcess.Filters.Item(1).Properties.Item("FormatID").Value = $wiaFormatPNG
		$image = $imageProcess.Apply($image)
	}

	# Build filepath from current user's desktop path and filename 'Scan 0'
	$filename = "$([Environment]::GetFolderPath("Desktop"))\Scan {0}.png"

	# If a file named 'Scan 0' already exists, increment the index as long as needed
	$index = 0
	while (test-path ($filename -f $index)) {
		[void](++$index)
	}
	$filename = $filename -f $index
	$image.SaveFile($filename)
}

function ConvertPDF {
	# Default app must be "photos" for this to work
    # Convert file to PDF by using 'Microsoft print to PDF' printer
    Write-Output 'Converting to PDF now...'

    # Build filepath from current user's desktop path and filename 'Scan 0'
    $newfilename = "$([Environment]::GetFolderPath("Desktop"))\Scan {0}.pdf"

    # If a file named 'Scan 0' already exists, increment the index as long as needed
	$index = 0
	while (test-path ($newfilename -f $index)) {
		[void](++$index)
	}
	$newfilename = $newfilename -f $index

	# This will open 'Microsoft print to PDF' dialog window, but during your first run,
	# make sure to immediately exit after opening it so you can select what printer to use within it
    Start-Process $filename -Verb Print | Out-Printer -name "Microsoft Print to PDF"
	# Exit
	# Send keystrokes to windows form
    Start-Sleep 2
    [System.Windows.Forms.Sendkeys]::SendWait("{ENTER}")
    Start-Sleep 1
    [System.Windows.Forms.Sendkeys]::SendWait($newfilename)
    [System.Windows.Forms.Sendkeys]::SendWait("{ENTER}")
    Start-Sleep 2

    # Delete original image
    Write-Output 'Deleting original PNG...'
    Remove-Item $filename

    # Open pdf
    & $newfilename

	if (! $?) {
		$Message = 'An error occurred'
		[System.Windows.MessageBox]::Show($Message,$Title,$Buttons,$Icon)
	}
}
#===============================================================================================================
# Ensure messageboxes appear outside of PS ISE
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName System.Windows.Forms

# Define portion or entire printer name and IP address
$NameRegex = 'example'
$IPregex = '192.168.1.123'

DefaultPrinter
Scan
ConvertPDF
