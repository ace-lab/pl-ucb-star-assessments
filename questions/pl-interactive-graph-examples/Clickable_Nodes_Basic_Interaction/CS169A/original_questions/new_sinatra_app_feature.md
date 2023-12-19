# From S15 Quiz 1

Ru B. Hacker wants to add a new feature to the Hangperson game in HW#1: the opportunity for the player to guess the word. If they guess wrong, they lose immediately; if they guess right, they win immediately. 

Write the action (handler method) in app.rb that implements this behavior and is accessible via the URI  `/guess_word`. Here are some reminders/assumptions you can make:

* All actions can assume that @game contains the current game state, and @game.word is the word being guessed. 
* Depending on the guess, you should call @game.lose! or  @game.win! to forcibly change the game state to losing or winning respectively.  (These methods change the state of the game itself, but they don't do anything in the SaaS part of the app.)

Assume that the form where the player inputs the word to be guessed contains a field that looks like this:

```html
<label for="my_guess">Try guessing the word:</label>
<input type="text" name="my_guess" id="my_guess"/>
Recall that the existing handlers in app.rb are:
get  '/new'    do ; ... ; end   # show screen with "New Game" button
post '/create' do ; ... ; end   # start new game
post '/guess'  do ; ... ; end   # process a guess letter
get  '/show'   do ; ... ; end   # show current state of game
get  '/win'    do ; ... ; end   # show "You win" & button for "New game"
get  '/lose'   do ; ... ; end   # show "You lose" & button for "New game"
```

# FILL IN YOUR CODE HERE for the guess_word handler.

NOT ALL BLANKS MAY NEED TO BE FILLED IN, but you shouldn't have to 
add any blanks.

```ruby

_____ '/guess_word' do
   attempted_guess = __________.downcase
   ______________
   if  _______________
     @game.lose!
     ________________
     ________________
   else
     @game.win!
     ________________
     ________________
   end
   ______________
   ______________
end
```

## Solution

```ruby
post ‘/guess_word’ do
	attempted_guess = params[:my_guess].downcase
	if attempted_guess!=@guess.word
		@game.lose!
		redirect ‘/lose’
	else
		@game.win!
		redirect ‘/win’
	end
end
```
