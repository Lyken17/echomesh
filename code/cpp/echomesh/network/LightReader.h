#ifndef __ECHOMESH_LIGHT_READER__
#define __ECHOMESH_LIGHT_READER__

#include <stdio.h>

#include <istream>
#include <vector>

#include "echomesh/base/Config.h"
#include "echomesh/network/ReadThread.h"

namespace echomesh {

class LightingWindow;
class ConfigMidiInput;
class ConfigMidiOutput;

class LightReader : public ReadThread, public MidiInputCallback {
 public:
  LightReader(LightingWindow* window, const String& commandLine);
  virtual ~LightReader();
  virtual void handleIncomingMidiMessage (MidiInput*, const MidiMessage&);

 private:
  virtual void quit();
  void clear();
  void config();
  void displayLights();
  void enforceSizes();
  void light();
  void midi();

  uint8 getLedColor(float color) const;

  LightingWindow* const lightingWindow_;
  FILE* file_;
  bool compressed_;
  ColorList colors_;
  ColorByteBank bytes_;
  ByteList colorBytes_;
  Config config_;
  ColorBytes rgbOrder_;
  float brightness_;
  bool configReceived_;
  ScopedPointer<ConfigMidiInput> midiInput_;
  ScopedPointer<ConfigMidiOutput> midiOutput_;

  DISALLOW_COPY_AND_ASSIGN(LightReader);
};


}  // namespace echomesh

#endif  // __ECHOMESH_LIGHT_READER__
