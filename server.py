import os
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/android':
            self.serve_android_page()
        elif self.path.startswith('/apps/'):
            super().do_GET()  # Serve static file from disk
        elif self.path == '/':
            self.serve_index_page()
        else:
            super().do_GET()  # Serve static content

    def serve_index_page(self):
        template_path = 'templates/index.html'
        self.serve_page(template_path, app_type=None)

    def serve_android_page(self):
        template_path = 'templates/android.html'
        self.serve_page(template_path, app_type="android")

    def serve_page(self, template_path, app_type):
        # Read template
        if os.path.exists(template_path):
            with open(template_path, 'r') as file:
                html = file.read()

            # Inject dynamic content from 'apps' directory
            apps_content = self.get_apps_content(app_type)

            # Replace the placeholder in the template with the apps content
            html = html.replace('{{apps_content}}', apps_content)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404, 'Template not found')

    def get_apps_content(self, app_type=None):
        apps_dir = 'apps'
        metadata_file = 'apps_metadata.json'

        # Load metadata from JSON file
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}

        content = ""
        categories = os.listdir(apps_dir)

        for category in categories:
            category_path = os.path.join(apps_dir, category)
            if os.path.isdir(category_path):
                # Get category metadata
                category_metadata = metadata.get(category, {})
                category_heading = category_metadata.get("heading", category.capitalize())

                # List apps in this category
                apps_metadata = category_metadata.get("apps", {})

                filtered_apps = [
                    (app_name, app_data) for app_name, app_data in apps_metadata.items()
                    if app_type is None or app_data.get("appType") == app_type
                ]

                # If there are no apps of the requested appType, skip
                if not filtered_apps:
                    continue

                # Add the category heading inside a <div class="subheading"> block
                content += f"""
                <div class="subheading">
                    <h4>{category_heading}</h4>
                </div>
                <div class='content-row'><div class='content'>
                """

                for app_name, app_metadata in filtered_apps:
                    download_url = f"/apps/{category}/{app_name}.apk"
                    description = app_metadata.get('description', 'No description available.')
                    icon_url = app_metadata.get('icon', '/static/app-icon.png')

                    # Add the onclick event with lightbox details
                    content += f"""
                        <div class="item" onclick="showLightbox('{app_name}', '{description}', '{download_url}')">
                            <div class="icon" style="background-image: url('{icon_url}');"></div>
                            <p>{app_name}</p>
                        </div>
                    """
                content += "</div></div>"
        return content

# Using ThreadingHTTPServer to handle multiple concurrent requests
def run(server_class=ThreadingHTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
