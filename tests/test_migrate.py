import pytest
from pytest_mock import MockerFixture
from tortoise import Tortoise

from aerich.ddl.mysql import MysqlDDL
from aerich.ddl.postgres import PostgresDDL
from aerich.ddl.sqlite import SqliteDDL
from aerich.exceptions import NotSupportError
from aerich.migrate import Migrate


def test_migrate(mocker: MockerFixture):
    mocker.patch("click.prompt", return_value=True)
    apps = Tortoise.apps
    models = apps.get("models")
    diff_models = apps.get("diff_models")
    if isinstance(Migrate.ddl, SqliteDDL):
        with pytest.raises(NotSupportError):
            Migrate.diff_models(diff_models, models, True)
            Migrate.diff_models(models, diff_models, False)
    else:
        Migrate.diff_models(diff_models, models)
        Migrate.diff_models(models, diff_models, False)
    if isinstance(Migrate.ddl, MysqlDDL):
        assert Migrate.upgrade_operators == [
            "ALTER TABLE `category` ADD `name` VARCHAR(200) NOT NULL",
            "ALTER TABLE `user` ADD UNIQUE INDEX `uid_user_usernam_9987ab` (`username`)",
            "ALTER  TABLE `user` CHANGE `last_login_at` `last_login` DATETIME(6) NOT NULL  COMMENT 'Last Login'",
        ]
        assert Migrate.downgrade_operators == [
            "ALTER TABLE `category` DROP COLUMN `name`",
            "ALTER TABLE `user` DROP INDEX `uid_user_usernam_9987ab`",
            "ALTER  TABLE `user` CHANGE `last_login` `last_login_at` DATETIME(6) NOT NULL  COMMENT 'Last Login'",
        ]
    elif isinstance(Migrate.ddl, PostgresDDL):
        assert Migrate.upgrade_operators == [
            'ALTER TABLE "category" ADD "name" VARCHAR(200) NOT NULL',
            'ALTER TABLE "user" ADD CONSTRAINT "uid_user_usernam_9987ab" UNIQUE ("username")',
            'ALTER TABLE "user" RENAME COLUMN "last_login_at" TO "last_login"',
        ]
        assert Migrate.downgrade_operators == [
            'ALTER TABLE "category" DROP COLUMN "name"',
            'ALTER TABLE "user" DROP CONSTRAINT "uid_user_usernam_9987ab"',
            'ALTER TABLE "user" RENAME COLUMN "last_login" TO "last_login_at"',
        ]
    elif isinstance(Migrate.ddl, SqliteDDL):
        assert Migrate.upgrade_operators == [
            'ALTER TABLE "category" ADD "name" VARCHAR(200) NOT NULL',
            'ALTER TABLE "user" ADD UNIQUE INDEX "uid_user_usernam_9987ab" ("username")',
        ]
        assert Migrate.downgrade_operators == []


def test_sort_all_version_files(mocker):
    mocker.patch(
        "os.listdir",
        return_value=[
            "1_datetime_update.json",
            "11_datetime_update.json",
            "10_datetime_update.json",
            "2_datetime_update.json",
        ],
    )

    Migrate.migrate_location = "."

    assert Migrate.get_all_version_files() == [
        "1_datetime_update.json",
        "2_datetime_update.json",
        "10_datetime_update.json",
        "11_datetime_update.json",
    ]
