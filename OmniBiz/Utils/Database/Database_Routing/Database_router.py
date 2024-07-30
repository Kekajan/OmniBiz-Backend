class DatabaseRouter:
    default_db_apps = {'auth', "authentication", "business", "owner", "notification", "daily_revenue", "super",
                       'contenttypes', 'admin', 'token_blacklist'}
    dynamic_db_apps = {"staff", "inventory", "billing", "performance", "suppliers", "cash_book"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.default_db_apps:
            return 'default'
        elif model._meta.app_label in self.dynamic_db_apps:
            return hints.get('database', None)
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.default_db_apps:
            return 'default'
        elif model._meta.app_label in self.dynamic_db_apps:
            return hints.get('database', None)
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if getattr(obj1, '_state', None) and getattr(obj2, '_state', None):
            if obj1._state.db in {None, 'default'} or obj2._state.db in {None, 'default'}:
                return True
        if (obj1._meta.app_label in self.default_db_apps and
                obj2._meta.app_label in self.default_db_apps):
            return True
        if (obj1._meta.app_label in self.dynamic_db_apps and
                obj2._meta.app_label in self.dynamic_db_apps):
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.default_db_apps:
            return db == 'default'
        if app_label in self.dynamic_db_apps:
            return db != 'default'
        return None
