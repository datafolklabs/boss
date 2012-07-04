"""Tests for boss.core.exc."""

import unittest
from nose.tools import eq_, raises
from boss.core import exc

class ExceptionTestCase(unittest.TestCase):
    @raises(exc.BossError)    
    def test_boss_error(self):
        try:
            raise exc.BossError("BossError Test")
        except exc.BossError as e:
            eq_(e.msg, "BossError Test")
            eq_(e.__str__(), "BossError Test")
            raise
    
    @raises(exc.BossConfigError)    
    def test_boss_config_error(self):
        try:
            raise exc.BossConfigError("BossConfigError Test")
        except exc.BossConfigError as e:
            eq_(e.msg, "BossConfigError Test")
            eq_(e.__str__(), "BossConfigError Test")
            raise
    
    @raises(exc.BossRuntimeError)    
    def test_boss_runtime_error(self):
        try:
            raise exc.BossRuntimeError("BossRuntimeError Test")
        except exc.BossRuntimeError as e:
            eq_(e.msg, "BossRuntimeError Test")
            eq_(e.__str__(), "BossRuntimeError Test")
            raise
    
    @raises(exc.BossArgumentError)    
    def test_boss_argument_error(self):
        try:
            raise exc.BossArgumentError("BossArgumentError Test")
        except exc.BossArgumentError as e:
            eq_(e.msg, "BossArgumentError Test")
            eq_(e.__str__(), "BossArgumentError Test")
            raise
    
    @raises(exc.BossTemplateError)    
    def test_boss_template_error(self):
        try:
            raise exc.BossTemplateError("BossTemplateError Test")
        except exc.BossTemplateError as e:
            eq_(e.msg, "BossTemplateError Test")
            eq_(e.__str__(), "BossTemplateError Test")
            raise
    