css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}
'''

bot_template = '''
<div class="chat-message bot" style="background: linear-gradient(to bottom, #2b2b2b 0%, #808080 100%);">
    <div class="avatar">
        <img src="https://m.media-amazon.com/images/I/51DBd7O6GEL.jpg" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user" style="background: linear-gradient(to bottom, #808080 0%, #2b2b2b 100%);">
    <div class="avatar">
        <img src="https://i.ibb.co/MptyJ4j/logo.png">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''

page = """
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        // Set the enter_pressed flag to true when the enter key is pressed
        Streamlit.setComponentValue(true);
    }
});
</script>
"""