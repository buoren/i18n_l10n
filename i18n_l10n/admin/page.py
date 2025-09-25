
from nicegui import ui
from ..database import DatabaseManager
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AdminPage:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.translation_tags = []
        self.refresh_data()

    def refresh_data(self):
        """Load all translation tags from the database."""
        try:
            logger.info("Starting to load translation tags from database...")
            # Get all translation tags with their translations
            self.translation_tags = self.db_manager.get_all_translation_tags()
            logger.info(f"Loaded {len(self.translation_tags)} translation tags")
            if self.translation_tags:
                logger.info(f"First tag: {self.translation_tags[0]}")
        except Exception as e:
            logger.error(f"Failed to load translation tags: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.translation_tags = []

    def render_page(self):
        """Render the admin page with translation tags."""
        ui.page('/admin')(self._create_admin_interface)
        
    def _create_admin_interface(self):
        """Create the admin interface."""
        # Refresh data when the page is accessed
        self.refresh_data()
        
        ui.html('<div style="max-width: 1200px; margin: 0 auto; padding: 20px;">')
        
        # Header
        ui.html('<h1 style="color: #1976d2; margin-bottom: 2rem;">Translation Tags Admin</h1>')
        
        # Refresh button
        with ui.row().classes('mb-4'):
            ui.button('Refresh Data', icon='refresh', on_click=self._refresh_and_update).classes('bg-blue-500 hover:bg-blue-600 text-white')
            ui.button('Add New Tag', icon='add', on_click=self._show_add_tag_dialog).classes('bg-green-500 hover:bg-green-600 text-white')
        
        # Stats
        ui.html(f'<div style="margin-bottom: 1rem; color: #666;">Total Tags: {len(self.translation_tags)}</div>')
        
        # Translation tags table
        if self.translation_tags:
            self._create_tags_table()
        else:
            ui.html('<div style="text-align: center; color: #999; padding: 2rem;">No translation tags found</div>')
        
        ui.html('</div>')

    def _create_tags_table(self):
        """Create the translation tags table."""
        with ui.card().classes('w-full'):
            ui.html('<h3 style="margin-bottom: 1rem;">Translation Tags</h3>')
            
            # Table container with CSS Grid
            ui.html('''
                <div style="display: grid; grid-template-columns: 80px 1fr 2fr 1.5fr 120px 120px; gap: 0; border: 1px solid #e5e7eb;">
                    <!-- Header Row -->
                    <div style="padding: 12px; background-color: #f3f4f6; font-weight: bold; border-bottom: 1px solid #d1d5db;">ID</div>
                    <div style="padding: 12px; background-color: #f3f4f6; font-weight: bold; border-bottom: 1px solid #d1d5db;">Application</div>
                    <div style="padding: 12px; background-color: #f3f4f6; font-weight: bold; border-bottom: 1px solid #d1d5db;">Tag</div>
                    <div style="padding: 12px; background-color: #f3f4f6; font-weight: bold; border-bottom: 1px solid #d1d5db;">Context</div>
                    <div style="padding: 12px; background-color: #f3f4f6; font-weight: bold; border-bottom: 1px solid #d1d5db;">Translations</div>
                    <div style="padding: 12px; background-color: #f3f4f6; font-weight: bold; border-bottom: 1px solid #d1d5db;">Actions</div>
            ''')
            
            # Table rows
            for i, tag in enumerate(self.translation_tags):
                self._create_tag_row_grid(tag, i)
            
            ui.html('</div>')

    def _create_tag_row_grid(self, tag: Dict[str, Any], row_index: int):
        """Create a row for a translation tag using CSS Grid."""
        # ID
        ui.html(f'<div style="padding: 12px; border-bottom: 1px solid #e5e7eb; background-color: {"#f9fafb" if row_index % 2 == 0 else "white"};">{tag.get("id", "N/A")}</div>')
        
        # Application
        ui.html(f'<div style="padding: 12px; border-bottom: 1px solid #e5e7eb; background-color: {"#f9fafb" if row_index % 2 == 0 else "white"};">{tag.get("application", "N/A")}</div>')
        
        # Tag
        ui.html(f'<div style="padding: 12px; border-bottom: 1px solid #e5e7eb; background-color: {"#f9fafb" if row_index % 2 == 0 else "white"}; font-family: monospace; word-break: break-all;">{tag.get("tag", "N/A")}</div>')
        
        # Context
        context = tag.get("context", "")
        if len(context) > 50:
            context = context[:47] + "..."
        ui.html(f'<div style="padding: 12px; border-bottom: 1px solid #e5e7eb; background-color: {"#f9fafb" if row_index % 2 == 0 else "white"}; word-break: break-word;">{context}</div>')
        
        # Translations count
        translations = tag.get("translations", [])
        ui.html(f'<div style="padding: 12px; border-bottom: 1px solid #e5e7eb; background-color: {"#f9fafb" if row_index % 2 == 0 else "white"}; text-align: center;">{len(translations)} languages</div>')
        
        # Actions
        ui.html(f'<div style="padding: 12px; border-bottom: 1px solid #e5e7eb; background-color: {"#f9fafb" if row_index % 2 == 0 else "white"}; text-align: center;">')
        
        # Create action buttons
        with ui.row().classes('justify-center gap-1'):
            ui.button('View', icon='visibility').classes('bg-blue-100 hover:bg-blue-200 text-blue-700 text-xs px-2 py-1').on('click', lambda t=tag: self._view_tag_details(t))
            ui.button('Edit', icon='edit').classes('bg-yellow-100 hover:bg-yellow-200 text-yellow-700 text-xs px-2 py-1').on('click', lambda t=tag: self._edit_tag(t))
            ui.button('Delete', icon='delete').classes('bg-red-100 hover:bg-red-200 text-red-700 text-xs px-2 py-1').on('click', lambda t=tag: self._delete_tag(t))
        
        ui.html('</div>')

    def _create_tag_row(self, tag: Dict[str, Any]):
        """Create a row for a translation tag (legacy method - kept for compatibility)."""
        with ui.row().classes('w-full p-2 border-b hover:bg-gray-50'):
            # ID
            ui.html(f'<div style="flex: 1;">{tag.get("id", "N/A")}</div>')
            
            # Application
            ui.html(f'<div style="flex: 2;">{tag.get("application", "N/A")}</div>')
            
            # Tag
            ui.html(f'<div style="flex: 3; font-family: monospace;">{tag.get("tag", "N/A")}</div>')
            
            # Context
            context = tag.get("context", "")
            if len(context) > 50:
                context = context[:47] + "..."
            ui.html(f'<div style="flex: 2;">{context}</div>')
            
            # Translations count
            translations = tag.get("translations", [])
            ui.html(f'<div style="flex: 2;">{len(translations)} languages</div>')
            
            # Actions
            with ui.html('<div style="flex: 1;">').classes('flex gap-2'):
                ui.button('View', icon='visibility').classes('bg-blue-100 hover:bg-blue-200 text-blue-700 text-sm px-2 py-1').on('click', lambda t=tag: self._view_tag_details(t))
                ui.button('Edit', icon='edit').classes('bg-yellow-100 hover:bg-yellow-200 text-yellow-700 text-sm px-2 py-1').on('click', lambda t=tag: self._edit_tag(t))
                ui.button('Delete', icon='delete').classes('bg-red-100 hover:bg-red-200 text-red-700 text-sm px-2 py-1').on('click', lambda t=tag: self._delete_tag(t))

    def _refresh_and_update(self):
        """Refresh data and update the display."""
        self.refresh_data()
        ui.notify('Data refreshed successfully', type='positive')

    def _show_add_tag_dialog(self):
        """Show dialog to add a new translation tag."""
        with ui.dialog() as dialog, ui.card():
            ui.html('<h3>Add New Translation Tag</h3>')
            
            application_input = ui.input('Application').classes('w-full')
            tag_input = ui.input('Tag').classes('w-full')
            context_input = ui.textarea('Context').classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600 text-white')
                ui.button('Add', on_click=lambda: self._add_tag(application_input.value, tag_input.value, context_input.value, dialog)).classes('bg-green-500 hover:bg-green-600 text-white')
        
        dialog.open()

    def _add_tag(self, application: str, tag: str, context: str, dialog):
        """Add a new translation tag."""
        if not application or not tag:
            ui.notify('Application and Tag are required', type='negative')
            return
        
        try:
            tag_id = self.db_manager.create_translation_tag(application, tag, context)
            if tag_id:
                ui.notify('Translation tag added successfully', type='positive')
                dialog.close()
                self.refresh_data()
            else:
                ui.notify('Failed to add translation tag', type='negative')
        except Exception as e:
            logger.error(f"Failed to add translation tag: {str(e)}")
            ui.notify(f'Error adding tag: {str(e)}', type='negative')

    def _view_tag_details(self, tag: Dict[str, Any]):
        """View detailed information about a translation tag."""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
            ui.html(f'<h3>Translation Tag Details: {tag.get("tag", "N/A")}</h3>')
            
            # Tag info
            with ui.card().classes('mb-4'):
                ui.html('<h4>Tag Information</h4>')
                ui.html(f'<p><strong>ID:</strong> {tag.get("id", "N/A")}</p>')
                ui.html(f'<p><strong>Application:</strong> {tag.get("application", "N/A")}</p>')
                ui.html(f'<p><strong>Tag:</strong> {tag.get("tag", "N/A")}</p>')
                ui.html(f'<p><strong>Context:</strong> {tag.get("context", "N/A")}</p>')
            
            # Translations
            translations = tag.get("translations", [])
            if translations:
                ui.html('<h4>Translations</h4>')
                with ui.card():
                    for translation in translations:
                        ui.html(f'<p><strong>{translation.get("language", "N/A")}:</strong> {translation.get("text", "N/A")}</p>')
            else:
                ui.html('<p>No translations available</p>')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Close', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600 text-white')
        
        dialog.open()

    def _edit_tag(self, tag: Dict[str, Any]):
        """Edit a translation tag."""
        ui.notify('Edit functionality not implemented yet', type='info')

    def _delete_tag(self, tag: Dict[str, Any]):
        """Delete a translation tag."""
        ui.notify('Delete functionality not implemented yet', type='info')