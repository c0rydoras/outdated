import random
from datetime import timedelta

from django.utils import timezone
from factory import Faker, Sequence, SubFactory, Trait, post_generation
from factory.django import DjangoModelFactory

from outdated.user.factories import UserFactory

from . import models

PROVIDERS = ["PIP", "NPM"]


class DependencyFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"ember-{n}")
    provider = random.choice(PROVIDERS)

    class Meta:
        model = models.Dependency
        django_get_or_create = ("name", "provider")


class ReleaseVersionFactory(DjangoModelFactory):
    class Meta:
        model = models.ReleaseVersion
        django_get_or_create = ("dependency", "major_version", "minor_version")

    dependency = SubFactory(DependencyFactory)
    end_of_life = Faker("date_this_year")
    major_version = random.randint(0, 10)
    minor_version = Sequence(lambda n: n)

    class Params:
        undefined = Trait(end_of_life=None)
        outdated = Trait(end_of_life=timezone.datetime.now().date())
        warning = Trait(
            end_of_life=timezone.datetime.now().date() + timedelta(days=150),
        )
        up_to_date = Trait(
            end_of_life=timezone.datetime.now().date() + timedelta(days=365),
        )


class VersionFactory(DjangoModelFactory):
    release_version = SubFactory(ReleaseVersionFactory)
    patch_version = Sequence(lambda n: n)
    release_date = Faker("date_this_year")

    class Meta:
        model = models.Version


class ProjectFactory(DjangoModelFactory):
    name = Faker("uuid4")
    repo = Sequence(lambda n: f"github.com/userorcompany/{n}/")
    repo_type = "public"

    @post_generation
    def versioned_dependencies(self, create, extracted, **kwargs):
        if not create:
            return  # pragma: no cover
        if extracted:
            for versioned_dependency in extracted:
                self.versioned_dependencies.add(versioned_dependency)

    class Meta:
        model = models.Project


class MaintainerFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    user = SubFactory(UserFactory)

    class Meta:
        model = models.Maintainer
