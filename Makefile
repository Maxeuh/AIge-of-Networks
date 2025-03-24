.PHONY: apidoc html clean cleanall help default

# Définir la cible par défaut
default: network_bridge

# Afficher l'aide
help:
	@echo "make : Compiler le programme network_bridge"
	@echo "make clean : Nettoyer les fichiers compilés de network_bridge"
	@echo "make doc : Construire la documentation HTML"
	@echo "make clean_doc : Nettoyer toutes les documentations"
	@echo "make cleanall : Nettoyer les fichiers compilés et les documentations"
	@echo "make apidoc : Générer les fichiers .rst avec sphinx-apidoc"
	@echo "make html : Construire la documentation HTML"
	@echo "make latex : Construire la documentation LATEX"
	@echo "make pdf : Construire la documentation PDF avec pdflatex"

# Compiler le programme network_bridge
CC=gcc
CFLAGS=-Wall -Wextra

# Détection du système d'exploitation
ifeq ($(OS),Windows_NT)
	# Configuration pour Windows
	CFLAGS += -D_WIN32
	LDFLAGS=-lws2_32 -liphlpapi
	EXE_EXT=.exe
	RM=del /Q
else
	# Configuration pour Unix/Linux/MacOS
	CFLAGS += -pthread
	LDFLAGS=
	EXE_EXT=
	RM=rm -f
endif

NETWORK_BRIDGE=network_bridge$(EXE_EXT)

network_bridge: network_bridge.c
	$(CC) $(CFLAGS) -o $(NETWORK_BRIDGE) network_bridge.c $(LDFLAGS)

clean:
	$(RM) $(NETWORK_BRIDGE)

# Générer les fichiers .rst avec sphinx-apidoc
apidoc:
	sphinx-apidoc -o docs/sphinx/source . -f

# Construire la documentation HTML
html: apidoc
	$(MAKE) -C docs/sphinx html

# Construire la documentation LATEX
latex: apidoc
	$(MAKE) -C docs/sphinx latex

# Construire la documentation PDF avec pdflatex
pdf: latex
	$(MAKE) -C docs/sphinx/_build/latex all-pdf

# Nettoyer la documentation Sphinx
clean_doc:
	rm -rf docs/sphinx/source
	rm -rf docs/sphinx/_build
	rm -rf docs/sphinx/_templates

# Construire la documentation HTML par défaut
doc: html

# Nettoyer toutes les documentations
cleanall: clean clean_doc