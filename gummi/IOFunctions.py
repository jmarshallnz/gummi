#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Copyright (c) 2009 Alexander van der Mey <alexvandermey@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import glib
import shutil
import tempfile


class IOFunctions:
	
	def __init__(self, config, statusbar, editorpane, motion):
		
		self.config = config
		self.editorpane = editorpane
		self.motion = motion

		self.statusbar = statusbar
		self.statusbar_cid = self.statusbar.get_context_id("Gummi")

		self.tempdir = os.environ.get("TMPDIR", "/tmp")
		self.filename = None
		self.texpath = None
		self.workfile = None
		self.pdffile = None

	def make_environment(self, filename=None):
		self.filename = filename
		self.create_envfiles(filename)
		env = self.return_envfiles()
		self.motion.update_envfiles(env)
		self.motion.initial_preview()
		#if self.config.get_bool("autosaving"):		
		#	self.reset_autosave()

	def create_envfiles(self, filename):
		if filename is not None:
			self.filename = filename
			self.texpath = os.path.dirname(self.filename) + "/"
			if ".tex" in self.filename:
				self.texname = os.path.basename(self.filename)[:-4]
			else:
				self.texname = os.path.basename(self.filename)
		self.workfile = tempfile.mkstemp(".tex")[1]
		self.pdffile = self.workfile[:-4] + ".pdf"
		print ("\nEnvironment created for: \n" + \
				"TEX: " + str(self.filename) + "\n" \
				"TMP: " + self.workfile + "\n" + \
				"PDF: " + self.pdffile + "\n")

	def load_default_text(self):
		self.editorpane.fill_buffer \
			(self.config.get_value("default_text", "welcome"))
		os.chdir(os.environ['HOME'])

	def load_file(self, filename):
		try:
			decode = self.editorpane.decode_text(filename)
			self.editorpane.fill_buffer(decode)
			self.filename = filename
			self.make_environment(self.filename)
			self.set_status("Loading file " + self.filename)

		except: print "load_file failed"

	def save_file(self, filename):
		try:		
			content = self.editorpane.grab_buffer()
			encoded = self.editorpane.encode_text(content)
			self.set_status("Saving file " + self.filename)
			fout = open(self.filename, "w")
			fout.write(encoded)
			fout.close()
		except: print "save_file failed"

	def export_pdffile(self):
		try:
			export = self.texpath + self.texname + ".pdf"
			shutil.copy2(self.pdffile, export)
			os.chdir(self.texpath)
		except IOError: pass

	def start_autosave(self, time):
		self.autosave = glib.timeout_add_seconds(time, self.autosave_document)

	def stop_autosave(self):
		try:
			glib.source_remove(self.autosave)
		except AttributeError: pass 

	def reset_autosave(self):
		self.stop_autosave()
		self.start_autosave(self.config.get_int("autosave_timer"))

	def autosave_document(self):
		if self.filename is not None:
			self.save_file(self.filename)
			self.set_status("Autosaving file " + self.filename)
		return True

	def set_status(self, message):
		self.statusbar.push(self.statusbar_cid, message)
		glib.timeout_add(4000, self.remove_status)

	def remove_status(self):
		self.statusbar.push(self.statusbar_cid, "")

	def filename(self):
		return self.filename

	def return_envfiles(self):
		return self.tempdir, \
				self.filename, \
				self.texpath, \
				self.workfile, \
				self.pdffile



