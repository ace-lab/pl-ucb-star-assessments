require_relative '../script.rb'

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
# load './add_pg13_to_movies.rb'
