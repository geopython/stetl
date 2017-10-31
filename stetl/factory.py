# -*- coding: utf-8 -*-

from util import Util

log = Util.get_log('factory')


class Factory:
    """
    Object and class Factory (Pattern).
    Based on: http://stackoverflow.com/questions/2226330/instantiate-a-python-class-from-a-name
    """

    def create_obj(self, configdict, section):
        class_obj_inst = None

        # Get value for 'class' property
        class_string = configdict.get(section, 'class')
        try:
            if not class_string:
                raise ValueError('Class name not defined in section %s.' % section)

            # class object from module.class name
            class_obj = self.class_forname(class_string)

            # class instance from class object with constructor args
            class_obj_inst = self.new_instance(class_obj, configdict, section)
        except Exception, e:
            log.error("cannot create object instance from class '%s' e=%s" % (class_string, str(e)))
            raise e

        return class_obj_inst

    def class_forname(self, class_string):
        """Returns class instance specified by a string.

        Args:
            class_string: The string representing a class.

        Raises:
            ValueError if module part of the class is not specified.
        """
        class_obj = None
        try:
            module_name, dot, class_name = class_string.rpartition('.')
            if module_name == '':
                raise ValueError('Class name must contain module part.')
            class_obj = getattr(
                __import__(module_name, globals(), locals(), [class_name], -1), class_name)
        except Exception, e:
            log.error("cannot create class '%s'" % class_string)
            raise e

        return class_obj

    def new_instance(self, class_obj, configdict, section):
        """Returns object instance from class instance.

        Args:
            class_obj: object representing a class instance.
            args: standard args.
            kwargs: standard args.
        """
        return class_obj(configdict, section)


factory = Factory()

# bar="bar"
# foo="foo"
# x = mkinst("factory.Foo", bar, 0, 4, disc="bust")
# y = mkinst("Bar", foo, batman="robin")
# = import_class("foo.Foo", foo)
#
# o = x(foo)
# x.p()
