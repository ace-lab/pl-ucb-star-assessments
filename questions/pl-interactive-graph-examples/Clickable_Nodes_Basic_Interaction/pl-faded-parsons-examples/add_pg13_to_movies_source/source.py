"""
<markdown>
# Add and validate a field on the RottenPotatoes Movie model

The MPAA rating PG-13 was introduced in 1984.  Enhance the Movie class to check that the "PG-13" rating is only accepted as valid if the movie was released on or after 1-Jan-1984.

Recall that:

* `validate :my_validation_method` calls the instance method my_validation_method on the model object to be validated

* The `release_date` attribute is a Ruby Time object; these can be compared directly using <=>, <, >, etc. You can create a Time object from a date string by saying Time.parse("1/1/1984"). You can assume the release_date is always valid.

* Calling `errors.add(:field, "message")` on the model object to be validated adds a validation error associated with the attribute named field, with the explanatory message message; for example, `errors.add(:title, "cannot be blank")`
</markdown>
"""

class Movie < ActiveRecord::Base
  validate :rating_consistent_with_date
  def ?rating_consistent_with_date?()
    pg13_invented = Time.parse "1 Jan 1984"
    if (?pg13_invented > self.release_date?) and (?self.rating == 'PG-13'?)
       ?self?.errors.add(:rating, 'only valid for 1984 and later')
    end
  end
end

## tests/app/script.rb ##
# require 'active_support/core_ext/time'
module ActiveRecord
  class Base
    class Errors
      def add(attr,str) ; end
    end
    cattr_accessor :validate_called
    attr_accessor :rating, :release_date
    attr_reader :validate_called, :errors
    def initialize(rating,release_date)
      @rating,@release_date = rating,release_date
      @errors = Errors.new
    end
    def self.validate(callable)
      @@validate_called = callable
    end
  end
end

## tests/app/script.rb ##

## tests/app/Gemfile ##
source 'https://www.rubygems.org'

gem 'rspec'
gem 'json'
gem 'rails'

## tests/app/Gemfile ##

## test ##
describe 'movie validation' do
  before(:each) do
    expect(Movie.validate_called.to_sym).to eq(:rating_consistent_with_date)
  end
  it 'gives error if pre-1984 movie has PG-13 rating' do
    @m = Movie.new("PG-13",Time.parse("31-Dec-1983"))
    expect(@m.errors).to receive(:add).with(:rating,'only valid for 1984 and later')
    expect { @m.rating_consistent_with_date }.not_to raise_error
  end
  it 'validates if post-1984 movie has PG-13 rating' do
    @m = Movie.new("PG-13",Time.parse("31-Dec-1984"))
    expect(@m.errors).not_to receive(:add)
    expect { @m.rating_consistent_with_date }.not_to raise_error
  end
end
# load student code here...defines Movie as subclass of fake AR::Base
load './add_pg13_to_movies.rb'

## test ##

# a comment
# another comment

