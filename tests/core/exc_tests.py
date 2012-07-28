"""Tests for boss.core.exc."""

from cement.utils import test
from boss.core import exc

class ExceptionTestCase(test.CementTestCase):
    @test.raises(exc.BossError)    
    def test_boss_error(self):
        try:
            raise exc.BossError("BossError Test")
        except exc.BossError as e:
            test.eq(e.msg, "BossError Test")
            test.eq(e.__str__(), "BossError Test")
            raise
    
    @test.raises(exc.BossConfigError)    
    def test_boss_config_error(self):
        try:
            raise exc.BossConfigError("BossConfigError Test")
        except exc.BossConfigError as e:
            test.eq(e.msg, "BossConfigError Test")
            test.eq(e.__str__(), "BossConfigError Test")
            raise
    
    @test.raises(exc.BossRuntimeError)    
    def test_boss_runtime_error(self):
        try:
            raise exc.BossRuntimeError("BossRuntimeError Test")
        except exc.BossRuntimeError as e:
            test.eq(e.msg, "BossRuntimeError Test")
            test.eq(e.__str__(), "BossRuntimeError Test")
            raise
    
    @test.raises(exc.BossArgumentError)    
    def test_boss_argument_error(self):
        try:
            raise exc.BossArgumentError("BossArgumentError Test")
        except exc.BossArgumentError as e:
            test.eq(e.msg, "BossArgumentError Test")
            test.eq(e.__str__(), "BossArgumentError Test")
            raise
    
    @test.raises(exc.BossTemplateError)    
    def test_boss_template_error(self):
        try:
            raise exc.BossTemplateError("BossTemplateError Test")
        except exc.BossTemplateError as e:
            test.eq(e.msg, "BossTemplateError Test")
            test.eq(e.__str__(), "BossTemplateError Test")
            raise
    