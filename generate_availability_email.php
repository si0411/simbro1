<?php
/**
 * Generate and view limited availability email
 */

// Change to the script directory
chdir(__DIR__);

// Set environment and run the Python script
$pythonScript = __DIR__ . '/generate_limited_availability_email.py';
$dataFile = __DIR__ . '/BT_scraping/group_tours_frontend_enhanced.json';

// Check if data file exists
if (!file_exists($dataFile)) {
    die('Error: Tour data file not found at: ' . htmlspecialchars($dataFile));
}

// Run the Python script and capture output
$command = "/usr/bin/python3 " . escapeshellarg($pythonScript) . " 2>&1";
$output = shell_exec($command);

// Find the generated HTML file
$files = glob(__DIR__ . '/limited_availability_email_*.html');
if (empty($files)) {
    die('Error: Email HTML file not generated.<br><br>Command: ' . htmlspecialchars($command) . '<br><br>Output:<br><pre>' . htmlspecialchars($output) . '</pre>');
}

// Get the most recent file
usort($files, function($a, $b) {
    return filemtime($b) - filemtime($a);
});

$htmlFile = $files[0];

// Read the HTML content
$htmlContent = file_get_contents($htmlFile);

// Output the HTML directly
header('Content-Type: text/html; charset=utf-8');
echo $htmlContent;
?>
