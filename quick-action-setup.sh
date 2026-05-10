#!/bin/bash
# Setup macOS Quick Action for right-click folder conversion

echo "🎬 Setting up macOS Quick Action"
echo "==================================="
echo ""

# Create workflow directory
WORKFLOW_DIR="$HOME/Library/Services/Convert DAV to MP4.workflow"
mkdir -p "$WORKFLOW_DIR/Contents"

# Create plist file
cat > "$WORKFLOW_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AMIsApplet</key>
	<true/>
	<key>AMStoreActionScript</key>
	<true/>
	<key>NSServices</key>
	<array>
		<dict>
			<key>NSMenuItem</key>
			<dict>
				<key>default</key>
				<string>Convert DAV to MP4</string>
			</dict>
			<key>NSMessage</key>
			<string>runWorkflowAsService</string>
			<key>NSSendTypes</key>
			<array>
				<string>NSFilenamesPboardType</string>
			</array>
		</dict>
	</array>
</dict>
</plist>
EOF

# Create workflow document
cat > "$WORKFLOW_DIR/Contents/document.wflow" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AMIsApplet</key>
	<true/>
	<key>AMStoreActionScript</key>
	<true/>
	<key>actions</key>
	<array>
		<dict>
			<key>action</key>
			<dict>
				<key>AMAccepts</key>
				<dict>
					<key>Container</key>
					<string>List</string>
					<key>Optional</key>
					<true/>
					<key>Types</key>
					<array>
						<string>com.apple.cocoa.path</string>
					</array>
				</dict>
				<key>AMActionVersion</key>
				<string>1.1.2</string>
				<key>AMApplication</key>
				<array>
					<string>Automator</string>
				</array>
				<key>AMParameterProperties</key>
				<dict>
					<key>source</key>
					<dict/>
				</dict>
				<key>AMProvides</key>
				<dict>
					<key>Container</key>
					<string>List</string>
					<key>Types</key>
					<array>
						<string>com.apple.cocoa.path</string>
					</array>
				</dict>
				<key>ActionBundlePath</key>
				<string>/System/Library/Automator/Run\ Shell\ Script.action</string>
				<key>ActionName</key>
				<string>Run Shell Script</string>
				<key>ActionParameters</key>
				<dict>
					<key>source</key>
					<string>python3 ~/dav-converter/dav_to_mp4_converter.py "$@" --replace-original --backup-dir ~/dav-converter/backups &amp;&amp; open ~/dav-converter</string>
				</dict>
				<key>BundleIdentifier</key>
				<string>com.apple.Automator.RunShellScript</string>
				<key>CFBundleVersion</key>
				<string>2.0.3</string>
				<key>CanShowWhenRun</key>
				<false/>
				<key>Category</key>
				<array>
					<string>AMCategoryUtilities</string>
				</array>
				<key>Class Name</key>
				<string>RunShellScriptAction</string>
				<key>InputUUID</key>
				<string>5F2D1B2E-0E8E-4A5E-8F5E-5F5F5F5F5F5F</string>
				<key>Keywords</key>
				<array>
					<string>Run</string>
					<string>Shell</string>
					<string>Script</string>
				</array>
				<key>OutputUUID</key>
				<string>5F2D1B2E-0E8E-4A5E-8F5E-5F5F5F5F5F60</string>
				<key>UUID</key>
				<string>5F2D1B2E-0E8E-4A5E-8F5E-5F5F5F5F5F5F</string>
				<key>compatibilityVersion</key>
				<integer>1</integer>
				<key>connectionErrorString</key>
				<string></string>
				<key>onlyShowWhenRunning</key>
				<false/>
				<key>showActionName</key>
				<true/>
				<key>showWhenRun</key>
				<false/>
			</dict>
			<key>isViewVisible</key>
			<true/>
			<key>location</key>
			<string>309.500000:342.000000</string>
			<key>nibPath</key>
			<string>/System/Library/Automator/Run\ Shell\ Script.action/Contents/Resources/English.lproj/main.nib</string>
		</dict>
	</array>
	<key>connectors</key>
	<dict/>
	<key>workflowMetaData</key>
	<dict>
		<key>workflowTypes</key>
		<array>
			<string>com.apple.Automator.workflow.gatekeeper.ubiquitous</string>
		</array>
	</dict>
</dict>
</plist>
EOF

echo "✅ Quick Action installed!"
echo ""
echo "Now right-click any folder and select:"
echo "Quick Actions → Convert DAV to MP4"
echo ""
echo "The workflow will:"
echo "  • Convert all DAV files to MP4"
echo "  • Replace originals with converted versions"
echo "  • Back up originals to ~/dav-converter/backups"
echo ""
echo "Note: You may need to restart Finder or log out/in for it to appear."
