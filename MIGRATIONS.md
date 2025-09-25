# Database Migrations with Alembic

This project uses Alembic for database schema management and migrations.

## 🚀 Quick Start

### **Create a New Migration**
```bash
# Create a new migration for schema changes
./scripts/create_migration.sh "Add user preferences table"

# Or with specific message
./scripts/create_migration.sh "Update translation table with new fields"
```

### **Apply Migrations**
```bash
# Apply all pending migrations
./scripts/migrate_local.sh upgrade

# Or apply to specific revision
python3 scripts/migrate.py upgrade 0002
```

### **Check Migration Status**
```bash
# Check current migration status
./scripts/migrate_local.sh current

# View migration history
./scripts/migrate_local.sh history
```

## 📁 **Migration Files**

- **`alembic.ini`** - Alembic configuration
- **`alembic/env.py`** - Migration environment setup
- **`alembic/versions/`** - Migration files directory
  - `0001_initial_schema.py` - Initial database schema
  - `0002_add_api_keys_table.py` - API keys table
- **`scripts/migrate.py`** - Migration management script

## 🔧 **Common Commands**

### **Local Development**
```bash
# Set up local environment
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=i18n_l10n_db
export DB_USER=appuser
export DB_PASSWORD=password

# Create migration
python3 scripts/migrate.py revision --message "Your message"

# Apply migrations
python3 scripts/migrate.py upgrade

# Check status
python3 scripts/migrate.py current
```

### **Production (Cloud SQL)**
```bash
# Set up production environment
export DB_CONNECTION_NAME=your-connection-name
export DB_NAME=i18n_l10n_db
export DB_USER=appuser
export DB_PASSWORD=your-password

# Apply migrations
python3 scripts/migrate.py upgrade
```

## 📝 **Migration Workflow**

### **1. Make Model Changes**
```python
# In i18n_l10n/database.py
class NewTable(Base):
    __tablename__ = 'new_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
```

### **2. Create Migration**
```bash
./scripts/create_migration.sh "Add new_table"
```

### **3. Review Migration**
Check the generated file in `alembic/versions/` and modify if needed.

### **4. Apply Migration**
```bash
# Local development
./scripts/migrate_local.sh upgrade

# Production
python3 scripts/migrate.py upgrade
```

## 🔄 **Migration States**

### **Current State**
```bash
python3 scripts/migrate.py current
```

### **Migration History**
```bash
python3 scripts/migrate.py history
```

### **Upgrade to Latest**
```bash
python3 scripts/migrate.py upgrade head
```

### **Downgrade One Step**
```bash
python3 scripts/migrate.py downgrade -1
```

## 🚨 **Important Notes**

### **Production Deployments**
- ✅ **Always test migrations locally first**
- ✅ **Backup database before major migrations**
- ✅ **Review generated migration files**
- ✅ **Use staging environment for testing**

### **Migration Best Practices**
- ✅ **One logical change per migration**
- ✅ **Use descriptive migration messages**
- ✅ **Test both upgrade and downgrade**
- ✅ **Never edit applied migrations**

### **Rollback Strategy**
```bash
# Rollback to previous version
python3 scripts/migrate.py downgrade -1

# Rollback to specific version
python3 scripts/migrate.py downgrade 0001
```

## 🔍 **Troubleshooting**

### **Migration Conflicts**
```bash
# Check current state
python3 scripts/migrate.py current

# View history
python3 scripts/migrate.py history

# Resolve conflicts manually
```

### **Failed Migrations**
```bash
# Check migration status
python3 scripts/migrate.py current

# Fix the migration file
# Then retry
python3 scripts/migrate.py upgrade
```

### **Database Connection Issues**
```bash
# Check environment variables
echo $DB_CONNECTION_NAME
echo $DB_NAME
echo $DB_USER

# Test connection
python3 -c "from i18n_l10n.database import db_manager; print('Connected!')"
```

## 📚 **Advanced Usage**

### **Custom Migration Scripts**
```python
# In alembic/versions/your_migration.py
def upgrade():
    # Custom upgrade logic
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")

def downgrade():
    # Custom downgrade logic
    op.execute("UPDATE users SET status = NULL WHERE status = 'active'")
```

### **Data Migrations**
```python
# For data migrations, use op.execute()
def upgrade():
    op.execute("""
        INSERT INTO new_table (name, created_at)
        SELECT name, created_at FROM old_table
    """)
```

### **Schema Changes**
```python
# Add column
op.add_column('users', sa.Column('phone', sa.String(20)))

# Drop column
op.drop_column('users', 'old_field')

# Rename column
op.alter_column('users', 'old_name', new_column_name='new_name')
```

## 🎯 **Integration with Deployment**

The deployment scripts automatically run migrations:

1. **Cloud SQL Setup** - Runs initial migration
2. **Cloud Run Deployment** - App runs migrations on startup
3. **Manual Migrations** - Use scripts for manual updates

## 📖 **Further Reading**

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Migrations](https://docs.sqlalchemy.org/en/20/orm/session_transactions.html)
- [Database Migration Best Practices](https://www.prisma.io/dataguide/types/relational/what-are-database-migrations)
