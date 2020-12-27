import pytest
from capri.core.context import Context
from capri.core.exceptions import (
    BadSignature,
    RegistrationExists,
    DependencyNotFound
)


def test_registration(app):
    class IInstance:
        pass

    class Instance(IInstance):
        pass

    class FooContext(Context):
        pass

    def instance_factory(context: Context):
        return Instance()

    def none_factory(context: Context):
        return None

    context = app.create_context()

    # Test register value
    app.register('foo', 'v1')
    value = context.get('v1')
    assert value == 'foo'

    # Test register factory on same iface with different name
    app.register(instance_factory, IInstance, factory=True)
    app.register(instance_factory, (IInstance, 'i2'), factory=True)
    instance1 = context.get(IInstance)
    instance2 = context.get((IInstance, 'i2'))
    assert isinstance(instance1, Instance)
    assert isinstance(instance2, Instance)
    assert instance2 != instance1

    # Test register factory on same iface with different name, in
    # a context other than root context
    app.register(
        instance_factory,
        IInstance,
        factory=True,
        ctx_iface=FooContext)
    app.register(
        instance_factory,
        (IInstance, 'i3'),
        factory=True,
        ctx_iface=FooContext)
    foo_context = app.create_context(factory=FooContext, iface=FooContext)
    foo_instance1 = foo_context.get(IInstance)
    foo_instance2 = foo_context.get((IInstance, 'i2'))
    foo_instance3 = foo_context.get((IInstance, 'i3'))
    assert isinstance(foo_context, FooContext)
    assert foo_instance1 != instance1
    assert foo_instance2 != instance2
    assert isinstance(foo_instance3, Instance)

    # Test can't get instance registered in a different context
    with pytest.raises(DependencyNotFound):
        context.get((IInstance, 'i3'))

    # Test multi
    app.register(
        instance_factory,
        (IInstance, 'i4'),
        factory=True)
    instances = context.get_all(IInstance)
    assert len(instances) == 3

    # Test that multi instances uses the cache
    _i1 = next((i for i, t in instances if t == IInstance), None)
    _i2 = next((i for i, t in instances if t == (IInstance, 'i2')), None)
    assert _i1 == instance1
    assert _i2 == instance2

    # Test that getting multi instances caches those instances
    _i4 = next((i for i, t in instances if t == (IInstance, 'i4')), None)
    instance4 = context.get((IInstance, 'i4'))
    assert instance4 == _i4

    # Test can't override existing factory
    with pytest.raises(RegistrationExists):
        app.register(instance_factory, (IInstance, 'i2'), factory=True)

    # Test forced factory override
    app.register(none_factory, (IInstance, 'i2'), factory=True, force=True)
    # Need to add a dummy iface because a base context has been
    # created already. It is an anti-pattern to define two 
    context = app.create_context(iface='override')
    _i2 = context.get((IInstance, 'i2'))
    assert _i2 is None


def test_annotated_factory(app):
    class IInstance:
        pass

    class Instance(IInstance):
        pass

    class IAnnotated:
        pass

    class INotAnnotated:
        pass

    class FooContext(Context):
        pass

    def annotated_factory(instance: IInstance):
        return instance

    def not_annotated_factory(instance):
        return instance

    def not_annotated_multi_factory(instance: IInstance, foo):
        return instance

    def instance_factory(context):
        return Instance()

    context = app.create_context(iface='test_annotated')

    app.register(instance_factory, IInstance, factory=True)
    app.register(annotated_factory, IAnnotated, factory=True)
    app.register(not_annotated_factory, INotAnnotated, factory=True)
    app.register(not_annotated_multi_factory, (INotAnnotated, 'multi'), factory=True)

    # Test factory with annotated argument
    instance = context.get(IInstance)
    annotated = context.get(IAnnotated)
    print(instance)
    print(annotated)
    assert isinstance(instance, Instance)
    assert isinstance(annotated, Instance)
    assert instance == annotated

    # Test factory with a single non-annotated arg.
    # A single arg unannotated factory receives the
    # context as it's sole argument.
    not_annotated = context.get(INotAnnotated)
    assert isinstance(not_annotated, Context)
    assert not_annotated == context

    # Test factory with multiple non-annotated arg.
    # Multi arg factory with at least one unannotated argument
    # will raise an error
    with pytest.raises(BadSignature):
        context.get((INotAnnotated, 'multi'))


def test_settings(app):
    settings = app.settings

    # Test set settings success
    settings.set('a.b', 'foo')
    assert isinstance(settings.get('a'), dict)
    assert settings.get('a.b') == 'foo'
    assert settings.get('a.c') is None

    # Test set settings error
    with pytest.raises(AssertionError):
        settings.set('a.b.c', 'bar')

    # Test delete settings
    del settings['a.b']
    assert settings.get('a.b') is None

    # Test set settings after delete
    settings.set('a.b.c', 'bar')
    assert settings.get('a.b.c') == 'bar'
