# Set your cross compile prefix with CROSS_COMPILE variable
CROSS_COMPILE ?=

CMDSEP = ;

CC ?=		$(CROSS_COMPILE)gcc
AR ?=		$(CROSS_COMPILE)ar
LD ?=		$(CROSS_COMPILE)ld
OBJDUMP ?=	$(CROSS_COMPILE)objdump
OBJCOPY ?=	$(CROSS_COMPILE)objcopy
SIZE ?=		$(CROSS_COMPILE)size
MAKE ?=		make

# Selects the install prefix directory
PREFIX ?= /usr/local
LOCAL_MSG_DBG ?= n
DBE_DBG ?= n

# General C/CPP flags
CFLAGS_USR = -std=gnu99 -O2
# We expect these variables to be appended to the possible
# command-line options
override CPPFLAGS +=
override CXXFLAGS +=

# Malamute 1.0.0 requires this to be defined
# as all of its API is in DRAFT state
CFLAGS_USR += -DMLM_BUILD_DRAFT_API -D__BOARD_AFCV3_1__

CFLAGS_DEBUG =

# Debug flags -D<flasg_name>=<value>
CFLAGS_DEBUG += -g

# Specific platform Flags
CFLAGS_PLATFORM = -Wall -Wextra -Werror
LDFLAGS_PLATFORM =

# Suppress warnings from preprocessor, such as the ones liberrhand emits
# when not setting DBG_LVL
ifeq ($(notdir $(CC)),$(filter $(notdir $(CC)),gcc cc))
CFLAGS_PLATFORM += -Wno-cpp
endif

ifeq ($(notdir $(CC)),clang)
CFLAGS_PLATFORM += -Wno-error=\#warnings
endif

# Libraries
LIBS = -lbpmclient -lacqclient -lhalcsclient -lmlm -lerrhand -lhutils -lczmq -lzmq

# General library flags -L<libdir>
LFLAGS = -L${PREFIX}/lib

# Include directories
INCLUDE_DIRS = -I. -I${PREFIX}/include

# Merge all flags. We expect tghese variables to be appended to the possible
# command-line options
override CFLAGS += $(CFLAGS_USR) $(CFLAGS_PLATFORM) $(CFLAGS_DEBUG) $(CPPFLAGS) $(CXXFLAGS)
override LDFLAGS += $(LDFLAGS_PLATFORM)

# Every .c file will must be a separate example
examples_SRC = $(wildcard *.c)
OUT = $(basename $(examples_SRC))

all: $(OUT)

%: %.c
	$(CC) $(LFLAGS) $(CFLAGS) $(INCLUDE_DIRS) $^ -o $@ $(LFLAGS) $(LIBS)

#BAD
clean:
	find . -iname "*.o" -exec rm '{}' \;

mrproper: clean
	rm -f $(OUT)

install:
	install -m 755 $(OUT) $(PREFIX)/bin

uninstall:
	rm -rf $(PREFIX)/bin/$(OUT)
