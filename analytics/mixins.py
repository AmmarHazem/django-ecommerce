from .signals import object_viewed_signal

class ObjectViewMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(ObjectViewMixin, self).get_context_data(*args, **kwargs)
        obj = context.get('object')
        if obj:
            object_viewed_signal.send(obj.__class__, instance = obj, request = self.request)
        return context