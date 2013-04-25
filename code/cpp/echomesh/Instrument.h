#ifndef __ECHOMESH_INSTRUMENT__
#define __ECHOMESH_INSTRUMENT__

#include "echomesh/Echomesh.h"
#include "echomesh/LightConfig.h"

namespace echomesh {

class Instrument : public Component {
 public:
  Instrument(const String& label, const LightDisplay& config)
      : label_(label),
        config_(config),
        color_(Colours::black),
        labelColor_(Colours::white) {
  }
  ~Instrument() {}

  void setConfig(const LightDisplay& config) {
    MessageManagerLock l;
    config_ = config;
    repaint();
  }

  void setColor(uint8 r, uint8 g, uint8 b) {
    if (r != color_.getRed() ||
        g != color_.getGreen() ||
        b != color_.getBlue()) {
      MessageManagerLock l;
      color_ = Colour(r, g, b);
      static const int GREY = (3 * 0xFF) / 2;
      labelColor_ = ((r + g + b) >= GREY) ? Colours::black : Colours::white;
      repaint();
    }
  }

  virtual void paint(Graphics& g) {
    g.setColour(color_);
    Rectangle<int> b = getLocalBounds();
    if (config_.isRect)
      g.fillRect(b);
    else
      g.fillEllipse(b.getX(), b.getY(), b.getWidth(), b.getHeight());

    if (config_.label) {
      b.reduce(config_.labelPadding.x / 2, config_.labelPadding.x / 2);
      g.setColour(labelColor_);
      g.drawFittedText(label_, b, Justification::centred, 1);
    }
  }

 private:
  const String label_;
  LightDisplay config_;
  Colour color_;
  Colour labelColor_;

  JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(Instrument)
};

}  // namespace echomesh

#endif  // __ECHOMESH_INSTRUMENT__
