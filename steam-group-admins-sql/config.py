# Configure this to your needs

# Set which database type to use
# db_type = 'sqlite'
db_type = 'mysql'
db_host = 'localhost'
db_database = 'sourcemod'
db_user = ''
db_pass = ''
db_timeout = None
db_port = None


# Add groups here
groups = [
    # Groups should be a list of dictionary entries that match the following
    # example. The list should be ordered by highest sourcemod priority to
    # lowest
    {
        # This will be the admin group name used in sourcemod
        'name' = 'Example Group',
        # Sourcemod admin flags
        'flags' = 'z',
        # Sourcemod immunity level
        'immunity' = 0,
        # Steam group ID
        'id' = 1234,
    },
]
