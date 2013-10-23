#include <stdio.h>
#include <fstream>
#include <iostream>
#include <istream>
#include <string>

#include "base64/base64.h"
#include "echomesh/component/LightingWindow.h"
#include "echomesh/network/LightController.h"
#include "echomesh/network/SocketLineGetter.h"
#include "echomesh/util/GetDevice.h"
#include "echomesh/util/Quit.h"
#include "rec/util/thread/MakeCallback.h"

namespace echomesh {

using namespace std;
using namespace rec::util::thread;

#if 0 && JUCE_LINUX

static const char DEVICE_NAME[] = "/dev/spidev0.0";
const int LATCH_BYTE_COUNT = 3;
uint8 LATCH[LATCH_BYTE_COUNT] = {0};

#endif

LightController::LightController(LightingWindow* wind, const Node& node)
    : lightingWindow_(wind),
      node_(node),
#if 0 && JUCE_LINUX
      file_(fopen(DEVICE_NAME, "w")),
#endif
      compressed_(true) {
}

LightController::~LightController() {
#if 0 && JUCE_LINUX
  fclose(file_);
#endif
}

void LightController::clear() {
  for (int i = 0; i < colors_.size(); ++i)
    colors_[i] = Colours::black;

  displayLights();
}

void LightController::enforceSizes() {
  if (colors_.size() != config_.light.count)
    colors_.resize(config_.light.count, Colours::black);

  if (colorBytes_.size() != 3 * config_.light.count)
    colorBytes_.resize(3 * config_.light.count, 0x80);
}

void LightController::config() {
  const Node& data = node_["data"];
  data >> config_;
  enforceSizes();

  for (int i = 0; i < 3; ++i)
    rgbOrder_[i] = config_.light.hardware.rgbOrder.find("rgb"[i]);

  lightingWindow_->setConfig(config_.light);
}

inline uint8 getSpiColor(uint8 color) {
  return color / 2 + 0x80;
}

uint8 LightController::getLedColor(float color) const {
  int c = static_cast<int>((color * brightness_ + 1) * 0x80);
  return static_cast<uint8>(jmin(c, 0xFF));
}

void LightController::displayLights() {
  lightingWindow_->setLights(colors_);
  if (config_.light.hardware.local)  // Do the lights in Python.
    return;

  if (compressed_) {
    for (int i = 0; i < config_.light.count; ++i) {
      const Colour& color = colors_[i];
      uint8* light = &colorBytes_[3 * i];
      light[rgbOrder_[0]] = getSpiColor(color.getRed());
      light[rgbOrder_[1]] = getSpiColor(color.getGreen());
      light[rgbOrder_[2]] = getSpiColor(color.getBlue());
    }
  } else {
    for (int i = 0; i < config_.light.count; ++i) {
      const Colour& color = colors_[i];
      uint8* light = &colorBytes_[3 * i];
      light[rgbOrder_[0]] = getLedColor(color.getFloatRed());
      light[rgbOrder_[1]] = getLedColor(color.getFloatGreen());
      light[rgbOrder_[2]] = getLedColor(color.getFloatBlue());
    }
  }

#if 0 && JUCE_LINUX
  fwrite(&colorBytes_.front(), 1, colorBytes_.size(), file_);
  fflush(file_);
  fwrite(LATCH, 1, 3, file_);
  fflush(file_);
#endif
}

void LightController::light() {
  compressed_ = true;
  string lights;
  const Node& lightNode = node_["data"];
  if (lightNode.size() == 1) {
    lightNode[0] >> lights;
  } else {
    for (int i = 0; i < lightNode.size(); ++i) {
      string lt;
      lightNode[i] >> lt;
      lights += lt;
    }
  }

  string lights2 = base64::decode(lights);

  if (lights2.size() != 3 * config_.light.count) {
    String msg = "Size " + String(int(lights.size())) +
      ", count " + String(config_.light.count);
    log(msg);
    return;
  }

  const char* data = lights2.data();
  const uint8* bytes = reinterpret_cast<const uint8*>(data);

  for (int i = 0; i < config_.light.count; ++i)
    colors_[i] = Colour(bytes[3 * i], bytes[3 * i + 1], bytes[3 * i + 2]);

  displayLights();
}

}  // namespace echomesh
