# From open-response-exam-questions repo


Ru B. Hacker wants to add a new feature to the Hangperson game: the
opportunity for the player to guess the word. If they guess wrong,
they lose immediately; if they guess right, they win immediately.  

Write the action (handler method) in `app.rb` that implements
this behavior and is accessible via the URI `/guess_word` with
an appropriate HTTP method (verb).

Here are some reminders/assumptions you can make:

*  `@game` contains the
    current game state, and `@game.word` is the word being
    guessed, guaranteed to be in all lowercase.
* Depending on the guess, you should call `@game.lose!` or
   `@game.win!` to forcibly change the game state to losing or
   winning respectively.  (But remember: these methods change the state of the game
   itself, but they don't do anything in the SaaS part of the app.)

* Assume that the form where the player inputs the word to be  guessed contains a field that looks like this:

```html
<label for="my_guess">Try guessing the word:</label>
<input type="text" name="my_guess" id="my_guess"/>
```

* If the player's guess is blank, it should be ignored and
       the player should be able to continue with the game.  (HINT:
       the method `to_s` can be safely called on a nil value
       to convert it to the empty string.)
       
Recall that the existing handlers in app.rb are as follows:

```
get  '/new' --- show screen with "New Game" button
post '/create' --- start new game
post '/guess' --- process a guess letter
get  '/show' --- show current state of game
get  '/win' --- show "You win" & button for "New game"
get  '/lose' --- show "You lose" & button for "New game"
```

Fill in your code below for the `guess_word` handler.

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
post 'guess_word' do
  attempted_guess = params['my_guess'].to_s.downcase
  redirect 'show' if attempted_guess == ''
  if attempted_guess != @game.guess
    @game.lose!
    redirect 'lose'
  else
    @game.win!
    redirect 'win'
  end
end
```
