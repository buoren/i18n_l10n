
from nicegui import ui
from ..database import get_db_manager
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class AdminPage:
    def __init__(self):
        self.translation_tags = []
        self.users = []
        self.refresh_data()

    def refresh_data(self):
        """Load all translation tags and users from the database."""
        try:
            logger.info("Starting to load translation tags from database...")
            # Get all translation tags with their translations
            self.translation_tags = get_db_manager().get_all_translation_tags()
            logger.info(f"Loaded {len(self.translation_tags)} translation tags")
            if self.translation_tags:
                logger.info(f"First tag: {self.translation_tags[0]}")
                
            # Get all users
            logger.info("Loading users from database...")
            self.users = self._get_all_users()
            logger.info(f"Loaded {len(self.users)} users")
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.translation_tags = []
            self.users = []

    def render_page(self):
        """Render the admin page with translation tags."""
        ui.page('/admin')(self._create_admin_interface)
        
    def _create_admin_interface(self):
        """Create the admin interface."""
        # Check authentication
        self._check_authentication()
        
        # Refresh data when the page is accessed
        self.refresh_data()
        
        ui.html('<div style="max-width: 1200px; margin: 0 auto; padding: 20px;">')
        
        # Header with user info and logout
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.html('<h1 style="color: #1976d2; margin: 0;">Translation Tags Admin</h1>')
            with ui.row().classes('items-center gap-4'):
                ui.html('<div id="user-info" style="color: #666;"></div>')
                ui.button('Logout', icon='logout', on_click=self._logout).classes('bg-red-500 hover:bg-red-600 text-white')
        
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
        
        # User management section
        ui.html('<div style="margin-top: 2rem;"></div>')
        ui.html(f'<h2 style="color: #1976d2; margin-bottom: 1rem;">User Management</h2>')
        ui.html(f'<div style="margin-bottom: 1rem; color: #666;">Total Users: {len(self.users)}</div>')
        
        # Users table
        if self.users:
            self._create_users_table()
        else:
            ui.html('<div style="text-align: center; color: #999; padding: 2rem;">No users found</div>')
        
        ui.html('</div>')
        
        # Load user info
        self._load_user_info()

    def _create_tags_table(self):
        """Create the translation tags table."""
        with ui.card().classes('w-full'):
            ui.html('<h3 style="margin-bottom: 1rem;">Translation Tags</h3>')
            
            # Get available language options
            from ..database import LanguageCode
            language_options = [{'label': f"{lang.value} ({lang.name})", 'value': lang.value} for lang in LanguageCode]
            
            # Prepare data for the table
            columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
                {'name': 'application', 'label': 'Application', 'field': 'application', 'align': 'left', 'sortable': True},
                {'name': 'tag', 'label': 'Tag', 'field': 'tag', 'align': 'left', 'sortable': True},
                {'name': 'context', 'label': 'Context', 'field': 'context', 'align': 'left', 'sortable': True},
                {'name': 'edit_translation', 'label': 'Edit Translation', 'field': 'edit_translation', 'align': 'left', 'sortable': False},
                {'name': 'language_select', 'label': 'Select Language', 'field': 'language_select', 'align': 'center', 'sortable': False},
                {'name': 'translation_text', 'label': 'Translation', 'field': 'translation_text', 'align': 'left', 'sortable': False},
                {'name': 'actions', 'label': 'Actions', 'field': 'actions', 'align': 'center', 'sortable': False}
            ]
            
            # Prepare rows data
            rows = []
            for tag in self.translation_tags:
                translations = tag.get("translations", [])
                context = tag.get("context", "")
                if len(context) > 50:
                    context = context[:47] + "..."
                
                # Create a mapping of language codes to translation texts
                translation_map = {t.get("language"): t.get("text", "") for t in translations}
                
                rows.append({
                    'id': tag.get("id", "N/A"),
                    'application': tag.get("application", "N/A"),
                    'tag': tag.get("tag", "N/A"),
                    'context': context,
                    'edit_translation': '',  # Text input for editing translation
                    'is_edit_mode': False,  # Track edit mode for this row
                    'language_select': '',  # Will be populated by dropdown
                    'translation_text': '',  # Will be populated by selected language
                    'translation_map': translation_map,  # Store the mapping for lookups
                    'actions': tag  # Store the full tag object for action buttons
                })
            
            # Create the table
            table = ui.table(
                columns=columns,
                rows=rows,
                row_key='id',
                selection='none',
                pagination={'rowsPerPage': 10}
            ).classes('w-full')
            
            # Add edit translation input to each row
            table.add_slot('body-cell-edit_translation', '''
                <q-td :props="props">
                    <q-input
                        v-model="props.row.edit_translation"
                        label="Translation Text"
                        placeholder="Enter translation..."
                        dense
                        outlined
                        :disable="!props.row.is_edit_mode"
                        @update:model-value="() => $parent.$emit('translation-input-changed', props.row)"
                    />
                </q-td>
            ''')
            
            # Add language selection dropdown to each row
            table.add_slot('body-cell-language_select', f'''
                <q-td :props="props">
                    <q-select
                        v-model="props.row.language_select"
                        :options="{language_options}"
                        label="Select Language"
                        dense
                        outlined
                        @update:model-value="() => $parent.$emit('language-changed', props.row)"
                    />
                </q-td>
            ''')
            
            # Add translation text display to each row
            table.add_slot('body-cell-translation_text', '''
                <q-td :props="props">
                    <div v-if="props.row.language_select && props.row.translation_map[props.row.language_select]">
                        {{ props.row.translation_map[props.row.language_select] }}
                    </div>
                    <div v-else-if="props.row.language_select" class="text-grey-5 italic">
                        No translation available
                    </div>
                    <div v-else class="text-grey-5 italic">
                        Select a language
                    </div>
                </q-td>
            ''')
            
            # Add action buttons to each row
            table.add_slot('body-cell-actions', '''
                <q-td :props="props">
                    <div class="flex justify-center gap-1">
                        <q-btn 
                            size="sm" 
                            :color="props.row.is_edit_mode ? 'green' : 'orange'"
                            :icon="props.row.is_edit_mode ? 'save' : 'edit'"
                            flat 
                            dense
                            @click="() => $parent.$emit('toggle-edit-mode', props.row)"
                        />
                        <q-btn 
                            size="sm" 
                            color="green" 
                            icon="add" 
                            flat 
                            dense
                            @click="() => $parent.$emit('add-translation', props.row)"
                        />
                        <q-btn 
                            size="sm" 
                            color="red" 
                            icon="delete" 
                            flat 
                            dense
                            @click="() => $parent.$emit('delete-tag', props.row.actions)"
                        />
                    </div>
                </q-td>
            ''')
            
            # Handle action events
            table.on('toggle-edit-mode', self._toggle_edit_mode)
            table.on('delete-tag', self._delete_tag)
            table.on('add-translation', self._add_translation)
            table.on('language-changed', self._on_language_changed)
            table.on('translation-input-changed', self._on_translation_input_changed)


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
            tag_id = get_db_manager().create_translation_tag(application, tag, context)
            if tag_id:
                ui.notify('Translation tag added successfully', type='positive')
                dialog.close()
                self.refresh_data()
            else:
                ui.notify('Failed to add translation tag', type='negative')
        except Exception as e:
            logger.error(f"Failed to add translation tag: {str(e)}")
            ui.notify(f'Error adding tag: {str(e)}', type='negative')


    def _delete_tag(self, tag: Dict[str, Any]):
        """Delete a translation tag."""
        ui.notify('Delete functionality not implemented yet', type='info')

    def _add_translation(self, row_data: Dict[str, Any]):
        """Add a new translation for a tag."""
        tag = row_data.get('actions', {})
        edit_text = row_data.get('edit_translation', '').strip()
        selected_language = row_data.get('language_select', '')
        
        # If there's text in the edit field and a language is selected, save that translation
        if edit_text and selected_language:
            try:
                from ..database import LanguageCode
                language_enum = LanguageCode(selected_language)
                
                success = get_db_manager().save_translation(
                    translation_tag_id=tag.get('id'),
                    language=language_enum,
                    text=edit_text,
                    is_plural=False,
                    plural_form=None,
                    author_id='admin'
                )
                
                if success:
                    ui.notify(f'Translation added for {selected_language}: {edit_text}', type='positive')
                    # Clear the edit field and exit edit mode
                    row_data['edit_translation'] = ''
                    row_data['is_edit_mode'] = False
                    self.refresh_data()
                else:
                    ui.notify('Failed to add translation', type='negative')
            except ValueError:
                ui.notify('Invalid language code', type='negative')
            except Exception as e:
                logger.error(f"Failed to add translation: {str(e)}")
                ui.notify(f'Error adding translation: {str(e)}', type='negative')
        
        # If no language is selected, show dialog to add translations for all languages
        elif not selected_language:
            with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
                ui.html(f'<h3>Add Translation for: {tag.get("tag", "N/A")}</h3>')
                
                # Get available language options
                from ..database import LanguageCode
                language_options = [{'label': f"{lang.value} ({lang.name})", 'value': lang.value} for lang in LanguageCode]
                
                # Language selection
                language_select = ui.select(
                    options=language_options,
                    label='Select Language',
                    value=language_options[0]['value'] if language_options else None
                ).classes('w-full mb-4')
                
                # Translation text
                translation_text = ui.textarea(
                    label='Translation Text',
                    placeholder='Enter the translated text...'
                ).classes('w-full mb-4')
                
                # Additional fields
                is_plural = ui.checkbox('Is Plural Form').classes('mb-4')
                plural_form = ui.input('Plural Form (if applicable)').classes('w-full mb-4')
                author_id = ui.input('Author ID', value='admin').classes('w-full mb-4')
                
                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600 text-white')
                    ui.button('Add Translation', on_click=lambda: self._save_translation(
                        tag, language_select.value, translation_text.value, 
                        is_plural.value, plural_form.value, author_id.value, dialog
                    )).classes('bg-green-500 hover:bg-green-600 text-white')
            
            dialog.open()
        
        # If there's no text in the edit field, show a message
        else:
            ui.notify('Please enter translation text in the edit field', type='info')

    def _save_translation(self, tag: Dict[str, Any], language: str, text: str, 
                         is_plural: bool, plural_form: str, author_id: str, dialog):
        """Save a new translation to the database."""
        if not language or not text:
            ui.notify('Language and translation text are required', type='negative')
            return
        
        try:
            from ..database import LanguageCode
            language_enum = LanguageCode(language)
            
            success = self.db_manager.save_translation(
                translation_tag_id=tag.get('id'),
                language=language_enum,
                text=text,
                is_plural=is_plural,
                plural_form=plural_form if is_plural else None,
                author_id=author_id
            )
            
            if success:
                ui.notify('Translation added successfully', type='positive')
                dialog.close()
                self.refresh_data()
            else:
                ui.notify('Failed to add translation', type='negative')
        except ValueError:
            ui.notify('Invalid language code', type='negative')
        except Exception as e:
            logger.error(f"Failed to add translation: {str(e)}")
            ui.notify(f'Error adding translation: {str(e)}', type='negative')

    def _on_language_changed(self, row_data: Dict[str, Any]):
        """Handle language selection change in the table."""
        # This method is called when a language is selected in the dropdown
        # The translation text will be automatically updated via Vue.js reactivity
        pass

    def _toggle_edit_mode(self, row_data: Dict[str, Any]):
        """Toggle edit mode for a row."""
        if row_data.get('is_edit_mode', False):
            # Save the translation if there's text and a language selected
            edit_text = row_data.get('edit_translation', '').strip()
            selected_language = row_data.get('language_select', '')
            
            if edit_text and selected_language:
                try:
                    from ..database import LanguageCode
                    language_enum = LanguageCode(selected_language)
                    
                    success = get_db_manager().save_translation(
                        translation_tag_id=row_data.get('actions', {}).get('id'),
                        language=language_enum,
                        text=edit_text,
                        is_plural=False,
                        plural_form=None,
                        author_id='admin'
                    )
                    
                    if success:
                        ui.notify(f'Translation saved for {selected_language}: {edit_text}', type='positive')
                        row_data['edit_translation'] = ''
                        self.refresh_data()
                    else:
                        ui.notify('Failed to save translation', type='negative')
                        return  # Don't exit edit mode if save failed
                except Exception as e:
                    logger.error(f"Failed to save translation: {str(e)}")
                    ui.notify(f'Error saving translation: {str(e)}', type='negative')
                    return  # Don't exit edit mode if save failed
            
            # Exit edit mode
            row_data['is_edit_mode'] = False
        else:
            # Enter edit mode
            row_data['is_edit_mode'] = True

    def _on_translation_input_changed(self, row_data: Dict[str, Any]):
        """Handle translation input changes."""
        # This method is called when the translation input changes
        # We can add any real-time validation or processing here if needed
        pass

    def _check_authentication(self):
        """Check if user is authenticated."""
        ui.add_body_html('''
        <script>
            // Check if user has a valid auth token
            const token = localStorage.getItem('auth_token');
            if (!token) {
                window.location.href = '/login';
                return;
            }
            
            // Verify token with server (simplified for now)
            // In a real app, you'd make an API call to verify the token
        </script>
        ''')
    
    def _load_user_info(self):
        """Load and display user information."""
        ui.add_body_html('''
        <script>
            // Load user info from token (simplified)
            const token = localStorage.getItem('auth_token');
            if (token) {
                try {
                    // Decode JWT token (simplified - in production, verify signature)
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    const userInfoDiv = document.getElementById('user-info');
                    if (userInfoDiv) {
                        userInfoDiv.innerHTML = `
                            <img src="${payload.picture || ''}" style="width: 32px; height: 32px; border-radius: 50%; margin-right: 8px;" />
                            <span>Welcome, ${payload.name || 'User'}</span>
                        `;
                    }
                } catch (e) {
                    console.error('Error decoding token:', e);
                    window.location.hrefhing  = '/login';
                }
            } else {
                window.location.href = '/login';
            }
        </script>
        ''')
    
    def _logout(self):
        """Handle user logout."""
        ui.add_body_html('''
        <script>
            // Clear auth token and redirect to login
            localStorage.removeItem('auth_token');
            window.location.href = '/logout';
        </script>
        ''')
        ui.navigate.to('/login')
    
    def _get_all_users(self):
        """Get all users from the database."""
        try:
            from ..database import User
            db_manager = get_db_manager()
            with db_manager.get_session() as session:
                users = session.query(User).order_by(User.created_at.desc()).all()
                return [{
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_active': user.is_active
                } for user in users]
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []
    
    def _create_users_table(self):
        """Create the users management table."""
        with ui.card().classes('w-full'):
            with ui.row().classes('w-full justify-between items-center mb-4'):
                ui.html('<h3 style="margin: 0;">Users</h3>')
                ui.button('', icon='add', on_click=self._show_add_user_dialog).classes('bg-green-500 hover:bg-green-600 text-white rounded-full w-10 h-10')
            
            # Prepare data for the table
            columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'left'},
                {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True, 'align': 'left'},
                {'name': 'email', 'label': 'Email', 'field': 'email', 'sortable': True, 'align': 'left'},
                {'name': 'created_at', 'label': 'Created At', 'field': 'created_at', 'sortable': True, 'align': 'left'},
                {'name': 'is_active', 'label': 'Active', 'field': 'is_active', 'sortable': True, 'align': 'center'},
            ]
            
            # Format the data for display
            rows = []
            for user in self.users:
                rows.append({
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'created_at': user['created_at'][:19] if user['created_at'] else 'N/A',
                    'is_active': '✓' if user['is_active'] else '✗',
                })
            
            # Create the table
            self.users_table = ui.table(
                columns=columns,
                rows=rows,
                row_key='id'
            ).classes('w-full')
            
            self.users_table.add_slot('body-cell-is_active', '''
                <q-td key="is_active" :props="props">
                    <span :style="props.value === '✓' ? 'color: green;' : 'color: red;'">
                        {{ props.value }}
                    </span>
                </q-td>
            ''')
    
    def _show_add_user_dialog(self):
        """Show dialog to add a new user."""
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.html('<h3 style="margin-top: 0;">Add New User</h3>')
            
            name_input = ui.input('Name', placeholder='Enter full name').classes('w-full')
            email_input = ui.input('Email', placeholder='Enter email address').classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600 text-white')
                ui.button('Add User', on_click=lambda: self._add_user(dialog, name_input.value, email_input.value)).classes('bg-green-500 hover:bg-green-600 text-white')
        
        dialog.open()
    
    def _add_user(self, dialog, name: str, email: str):
        """Add a new user to the database."""
        if not name or not email:
            ui.notify('Please fill in all fields', type='negative')
            return
        
        try:
            from ..database import User
            from datetime import datetime
            
            db_manager = get_db_manager()
            with db_manager.get_session() as session:
                # Check if user already exists
                existing_user = session.query(User).filter(User.email == email).first()
                if existing_user:
                    ui.notify(f'User with email {email} already exists', type='negative')
                    return
                
                # Create new user
                new_user = User(
                    name=name,
                    email=email,
                    created_at=datetime.utcnow(),
                    is_active=True
                )
                
                session.add(new_user)
                session.commit()
                
                ui.notify(f'Successfully added user: {name}', type='positive')
                dialog.close()
                
                # Refresh the data and update the table
                self.refresh_data()
                self._refresh_users_table()
                
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            ui.notify(f'Error adding user: {str(e)}', type='negative')
    
    def _refresh_users_table(self):
        """Refresh the users table display."""
        if hasattr(self, 'users_table'):
            # Prepare updated data
            rows = []
            for user in self.users:
                rows.append({
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'created_at': user['created_at'][:19] if user['created_at'] else 'N/A',
                    'is_active': '✓' if user['is_active'] else '✗',
                })
            
            # Update the table
            self.users_table.rows = rows
            self.users_table.update()