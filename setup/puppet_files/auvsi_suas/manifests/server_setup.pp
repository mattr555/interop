# AUVSI SUAS Puppet Module: server_setup
# Prepares server for running
# ==============================================================================

class auvsi_suas::server_setup {
    # First install the server
    require auvsi_suas::server_install
    # ... and the database
    require auvsi_suas::postgresql_setup

    # Prepare database
    exec { 'migrate':
        command => "python manage.py migrate --noinput",
        cwd => "/interop/server/",
    }

    # Copy all static files
    exec { 'collectstatic':
        command => "python manage.py collectstatic --noinput",
        cwd => "/interop/server/",
    }

    # Load initial testadmin superuser
    exec { 'testadmin superuser':
        command => "python manage.py loaddata fixtures/testadmin_superuser.yaml",
        cwd => "/interop/server/",
    }
}