#include "/development/echomesh/code/cpp/echomesh/component/InstrumentComponent.h"

namespace echomesh {

InstrumentComponent::InstrumentComponent()
    : color_(Colours::black), labelColor_(Colours::white) {
}

void InstrumentComponent::configure(const String& label,
                                    const Instrument& config) {
  MessageManagerLock l;
  config_ = config;
  label_ = label;
  repaint();
}

void InstrumentComponent::setColor(uint8 r, uint8 g, uint8 b) {
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

void InstrumentComponent::setColor(const Colour& c) {
  setColor(c.getRed(), c.getGreen(), c.getBlue());
}

void InstrumentComponent::paint(Graphics& g) {
  g.setColour(color_);
  Rectangle<int> b = getLocalBounds();
  if (config_.isRect)
    g.fillRect(b);
  else
    g.fillEllipse(b.getX(), b.getY(), b.getWidth(), b.getHeight());

  if (config_.label) {
    b.reduce(config_.labelPadding.x / 2, config_.labelPadding.y / 2);
    g.setColour(labelColor_);
    g.drawFittedText(label_, b, Justification::centred, 1);
  }
}

}  // namespace echomesh
