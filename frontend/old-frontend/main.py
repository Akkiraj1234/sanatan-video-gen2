import time
import mesop as me



# styles and css ==============================================================================================
box1_style = me.Style(
    background="#121212",
    min_height="calc(100%)",
    padding=me.Padding(bottom=16),
)

box2_style = me.Style(
    background="#121212",
    width="50%",
    margin=me.Margin.symmetric(horizontal="auto"),
    padding=me.Padding.symmetric(
        horizontal=16,
    ),
)
header_style = me.Style(
    padding = me.Padding(
        top = 64,
        bottom = 36,
    ),
)

header_text_style = me.Style(
        font_size=36,
        font_weight=700,
        background="linear-gradient(90deg, #4285F4, #AA5CDB, #DB4437) text",
        color="transparent",
)

def example_box_style(is_mobile):
    return me.Style(
        display="flex",
        flex_direction = "column" if is_mobile else "row",
        gap=24,
        margin=me.Margin(bottom=36),
    )

def example_box_column_style(is_mobile):
    return me.Style(
        width="100%" if is_mobile else 200,
        height=140,
        background="#F0F4F9",
        padding=me.Padding.all(16),
        font_weight=500,
        line_height="1.5",
        border_radius=16,
        cursor="pointer",
    )
    
chat_input_style = me.Style(
    padding=me.Padding.all(8),
    background="white",
    display="flex",
    width="100%",
    border=me.Border.all(
    me.BorderSide(width=0, style="solid", color="black")
    ),
    border_radius=12,
    box_shadow="0 10px 20px #0000000a, 0 2px 6px #0000000a, 0 0 1px #0000000a",
)

    
# the main app ================================================================================================

@me.stateclass
class State:
    input: str
    output: str
    in_progress: bool

def header_text():
    heading_text = "Sanatan videogen"
    with me.box(style = header_style):
        me.text(
            text = heading_text,
            style = header_text_style
        )

def example_row():
    EXAMPLES = [
        "How to tie a shoe",
        "Make a brownie recipe",
        "Write an email asking for a sick day off",
    ]
    is_mobile = me.viewport_size().width < 640
    with me.box(style = example_box_style(is_mobile)):
        for example in EXAMPLES:
            example_box(example, is_mobile)

def chat_input():
    state = me.state(State)
    with me.box(style = chat_input_style):
        with me.box(style=me.Style(flex_grow=1)):
            me.native_textarea(
                value = state.input,
                autosize = True,
                min_rows = 4,
                placeholder = "Enter your prompt",
                style = me.Style(
                    padding = me.Padding(top=16, left=16),
                    background = "white",
                    outline = "none",
                    width = "100%",
                    overflow_y = "auto",
                    border = me.Border.all(
                        me.BorderSide(style="none"),
                    ),
                ),
                on_blur=textarea_on_blur,
            )
        
        with me.content_button(type="icon", on_click=click_send):
            me.icon("send")

def output():
    output_box_style = me.Style(
        background="#F0F4F9",
        padding=me.Padding.all(16),
        border_radius=16,
        margin=me.Margin(top=36),
    )
    state = me.state(State)
    if state.output or state.in_progress:
        with me.box(style=output_box_style):
            if state.output:
                me.markdown(state.output)
            if state.in_progress:
                with me.box(style=me.Style(margin=me.Margin(top=16))):
                    me.progress_spinner()

def example_box(example: str, is_mobile: bool):
    with me.box(
        style=example_box_column_style(is_mobile), key=example, on_click=click_example_box):
        me.text(example)

def click_example_box(e: me.ClickEvent):
  state = me.state(State)
  state.input = e.key

def textarea_on_blur(e: me.InputBlurEvent):
  state = me.state(State)
  state.input = e.value

def click_send(e: me.ClickEvent):
  state = me.state(State)
  if not state.input:
    return
  state.in_progress = True
  input = state.input
  state.input = ""
  yield

  for chunk in call_api(input):
    state.output += chunk
    yield
  state.in_progress = False
  yield

def call_api(input):
  # Replace this with an actual API call
  time.sleep(60)
  yield "Example of streaming an output"
  time.sleep(1)
  yield "\n\nOutput: " + input



@me.page(path="/home/video_gen")
def page():
    with me.box(style = box1_style):
        with me.box(style = box2_style):
            header_text()
            example_row()
            chat_input()
            output()
            
    
